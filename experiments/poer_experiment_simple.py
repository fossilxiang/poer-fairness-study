#!/usr/bin/env python3
"""
PoER: Proof of Entropy Reduction - 简化实验版（仅用标准库）
"""

import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
import random
import math

@dataclass
class Household:
    household_id: int
    sorting_accuracy: float
    waste_generation: float
    participation_rate: float

def compute_entropy(prob_vec):
    """计算信息熵"""
    prob_vec = [p for p in prob_vec if p > 0]
    if len(prob_vec) == 0:
        return 0.0
    return -sum(p * math.log2(p) for p in prob_vec)

def generate_confusion_matrix(K, accuracy, rng):
    """生成混淆矩阵"""
    A = [[0.0] * K for _ in range(K)]
    for j in range(K):
        A[j][j] = accuracy
        for k in range(K):
            if j != k:
                A[j][k] = (1 - accuracy) / (K - 1)
    # 归一化
    for j in range(K):
        row_sum = sum(A[j])
        for k in range(K):
            A[j][k] /= row_sum
    return A

def poer_allocation(reports, baseline, alpha=100.0, version='original'):
    """
    PoER 积分分配
    
    version: 'original' - 原始版本
             'normalized' - 基线归一化版本 (PoER++)
    """
    K = len(baseline)
    M = list(baseline)
    credits = {}
    
    # 预计算基线熵（用于归一化）
    baseline_total = sum(baseline)
    H_baseline = compute_entropy([x/baseline_total for x in baseline]) if baseline_total > 0 else 1.0
    
    for house_id, m in reports:
        prior_total = sum(M)
        if prior_total == 0:
            H_prior = compute_entropy([x/prior_total if prior_total > 0 else 0 for x in M])
        else:
            H_prior = compute_entropy([x/prior_total for x in M])
        
        M = [M[k] + m[k] for k in range(K)]
        post_total = sum(M)
        H_post = compute_entropy([x/post_total for x in M])
        
        delta_H = max(0.0, H_prior - H_post)
        W = sum(m)
        
        if version == 'normalized':
            # PoER++: 基线归一化 + 对数平滑
            delta_H_norm = delta_H / (H_baseline + 0.01)  # 归一化到 [0,1]
            W_smooth = math.log(1 + W)  # 对数平滑，减少大户优势
            credit = alpha * delta_H_norm * W_smooth
        else:
            # 原始版本
            credit = alpha * delta_H * W
        
        credits[house_id] = credits.get(house_id, 0.0) + credit
    
    return credits

def weight_allocation(reports, beta=10.0):
    """按重量分配"""
    credits = {}
    for house_id, m in reports:
        W = sum(m)
        credits[house_id] = credits.get(house_id, 0.0) + beta * W
    return credits

def category_allocation(reports, weights, gamma=10.0):
    """按类别分配"""
    credits = {}
    for house_id, m in reports:
        credit = gamma * sum(m[k] * weights[k] for k in range(len(m)))
        credits[house_id] = credits.get(house_id, 0.0) + credit
    return credits

def gini_coefficient(values):
    """基尼系数"""
    if len(values) == 0 or sum(values) == 0:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    cumsum = sum((i + 1) * v for i, v in enumerate(sorted_vals))
    gini = (2 * cumsum) / (n * sum(sorted_vals)) - (n + 1) / n
    return max(0, min(1, gini))

def run_experiment(N=500, K=5, num_slots=30, seed=42):
    """运行实验"""
    random.seed(seed)
    np.random.seed(seed)
    
    print(f"开始 PoER 仿真实验...")
    print(f"  家庭数：{N}, 类别数：{K}, 轮数：{num_slots}")
    
    # 初始化家庭
    households = []
    for i in range(N):
        accuracy = max(0.3, min(0.95, random.gauss(0.7, 0.15)))
        waste_gen = max(0.5, min(5.0, random.lognormvariate(1.5, 0.3)))
        participation = random.betavariate(2, 2)
        households.append(Household(i, accuracy, waste_gen, participation))
    
    # 基准组分和碳因子
    baseline = [0.4, 0.25, 0.05, 0.1, 0.2]
    carbon_mix = [0.5, 0.3, 0.8, 0.2, 0.6]
    carbon_sorted = [0.1, -0.2, 0.3, 0.05, 0.5]
    
    # 调整 alpha 使 PoER 积分与其他机制数量级一致
    # 预实验：delta_H 约 0.001-0.01, W 约 2-5, 需要 alpha≈10000 才能匹配
    alpha_poer = 10000.0
    
    results = {
        'carbon_reduction': [],
        'utility_poer': [],
        'utility_poer_plus': [],
        'utility_weight': [],
        'utility_category': [],
        'gini_poer': [],
        'gini_poer_plus': [],
        'gini_weight': [],
        'gini_category': []
    }
    
    for slot in range(num_slots):
        reports = []
        total_carbon = 0.0
        
        for hh in households:
            if random.random() > hh.participation_rate:
                continue
            
            # 生成组分
            waste_comp = [baseline[k] + random.gauss(0, 0.05) for k in range(K)]
            waste_comp = [max(0.01, w) for w in waste_comp]
            total = sum(waste_comp)
            waste_comp = [w/total for w in waste_comp]
            
            # 混淆矩阵
            conf_mat = generate_confusion_matrix(K, hh.sorting_accuracy, random)
            
            # 分类后分布
            sorted_comp = [sum(waste_comp[j] * conf_mat[j][k] for j in range(K)) for k in range(K)]
            
            # 各桶质量
            sorted_mass = [sorted_comp[k] * hh.waste_generation for k in range(K)]
            
            # 碳减排
            carbon_before = sum(waste_comp[k] * carbon_mix[k] for k in range(K))
            carbon_after = sum(sorted_comp[k] * carbon_sorted[k] for k in range(K))
            carbon_red = max(0, (carbon_before - carbon_after) * hh.waste_generation)
            
            reports.append((hh.household_id, sorted_mass))
            total_carbon += carbon_red
        
        # 四种分配机制（新增 PoER++ 改进版）
        poer_cred = poer_allocation(reports, [b * 100 for b in baseline], alpha_poer, version='original')
        poer_plus_cred = poer_allocation(reports, [b * 100 for b in baseline], alpha_poer, version='normalized')
        weight_cred = weight_allocation(reports, 10.0)
        cat_weights = [0.8, 1.2, 1.0, 0.9, 0.5]
        category_cred = category_allocation(reports, cat_weights, 10.0)
        
        # 计算 Fehr-Schmidt 效用（包含公平偏好）
        def calc_fs_utility(credits, alpha_fs=0.5, beta_fs=0.3):
            """
            Fehr-Schmidt 不公平厌恶效用函数
            U_i = x_i - alpha * max(x_j - x_i, 0) - beta * max(x_i - x_j, 0)
            alpha: 嫉妒参数 ( disadvantageous inequality)
            beta: 内疚参数 (advantageous inequality)
            """
            if not credits:
                return 0.0
            values = list(credits.values())
            n = len(values)
            total_utility = 0.0
            for i, x_i in enumerate(values):
                u_i = x_i
                for j, x_j in enumerate(values):
                    if i != j:
                        if x_j > x_i:
                            u_i -= alpha_fs * (x_j - x_i)
                        elif x_i > x_j:
                            u_i -= beta_fs * (x_i - x_j)
                total_utility += u_i / n
            return total_utility
        
        results['carbon_reduction'].append(total_carbon)
        results['utility_poer'].append(calc_fs_utility(poer_cred))
        results['utility_poer_plus'].append(calc_fs_utility(poer_plus_cred))
        results['utility_weight'].append(calc_fs_utility(weight_cred))
        results['utility_category'].append(calc_fs_utility(category_cred))
        results['gini_poer'].append(gini_coefficient(list(poer_cred.values())))
        results['gini_poer_plus'].append(gini_coefficient(list(poer_plus_cred.values())))
        results['gini_weight'].append(gini_coefficient(list(weight_cred.values())))
        results['gini_category'].append(gini_coefficient(list(category_cred.values())))
        
        if (slot + 1) % 10 == 0:
            print(f"  完成第 {slot + 1}/{num_slots} 轮")
    
    # 统计摘要
    summary = {
        'avg_carbon_reduction': float(np.mean(results['carbon_reduction'])),
        'std_carbon_reduction': float(np.std(results['carbon_reduction'])),
        'avg_utility_poer': float(np.mean(results['utility_poer'])),
        'avg_utility_poer_plus': float(np.mean(results['utility_poer_plus'])),
        'avg_utility_weight': float(np.mean(results['utility_weight'])),
        'avg_utility_category': float(np.mean(results['utility_category'])),
        'avg_gini_poer': float(np.mean(results['gini_poer'])),
        'avg_gini_poer_plus': float(np.mean(results['gini_poer_plus'])),
        'avg_gini_weight': float(np.mean(results['gini_weight'])),
        'avg_gini_category': float(np.mean(results['gini_category'])),
        'utility_gain_poer_vs_weight': float((np.mean(results['utility_poer']) - np.mean(results['utility_weight'])) / np.mean(results['utility_weight']) * 100),
        'utility_gain_poer_plus_vs_weight': float((np.mean(results['utility_poer_plus']) - np.mean(results['utility_weight'])) / np.mean(results['utility_weight']) * 100),
        'fairness_improvement_poer_vs_weight': float((np.mean(results['gini_weight']) - np.mean(results['gini_poer'])) / np.mean(results['gini_weight']) * 100),
        'fairness_improvement_poer_plus_vs_weight': float((np.mean(results['gini_weight']) - np.mean(results['gini_poer_plus'])) / np.mean(results['gini_weight']) * 100)
    }
    
    print("\n实验结果摘要:")
    for k, v in summary.items():
        print(f"  {k}: {v:.4f}")
    
    return results, summary

if __name__ == '__main__':
    results, summary = run_experiment(N=500, K=5, num_slots=30, seed=42)
    
    # 保存结果
    output_dir = Path('/home/admin/.openclaw/workspace/poer_experiments/outputs')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / 'results.json', 'w', encoding='utf-8') as f:
        json.dump({'results': results, 'summary': summary}, f, indent=2)
    
    print(f"\n结果已保存至：{output_dir / 'results.json'}")
