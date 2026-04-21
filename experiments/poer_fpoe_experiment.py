#!/usr/bin/env python3
"""
F-PoER: Federated Proof of Entropy Reduction
改进版：滑动窗口 + 归一化 + 延迟结算

关键改进：
1. 时间分片（4 小时/窗口）- 消除先发优势
2. 积分池归一化 - 解决数量级坍塌
3. 延迟结算 - 窗口结束后统一分配
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

def fpoe_allocation_window(reports_window, baseline, total_carbon_credit, alpha=1.0):
    """
    F-PoER 单窗口积分分配（相对熵减 + 基础保障）
    
    关键改进：
    1. 50% 积分池按参与率平均分配（基础保障）
    2. 50% 积分池按相对熵减分配（激励精准分类）
    3. 相对熵减 = 该户熵减 / 窗口平均熵减
    
    Args:
        reports_window: 窗口内所有投放报告 [(house_id, mass_vector), ...]
        baseline: 基准组分
        total_carbon_credit: 窗口总积分池（基于碳减排量）
        alpha: 调节因子
    
    Returns:
        credits: {house_id: credit}
    """
    K = len(baseline)
    M_base = list(baseline)  # 固定基线（窗口内不变）
    
    # 计算基线熵
    base_total = sum(M_base)
    H_base = compute_entropy([x/base_total for x in M_base]) if base_total > 0 else 0.0
    
    # 第一步：并行计算每户的独立熵减
    house_deltas = {}
    house_weights = {}
    
    for house_id, m in reports_window:
        # 独立计算：基线 + 该户投放
        M_combined = [M_base[k] + m[k] for k in range(K)]
        combined_total = sum(M_combined)
        H_combined = compute_entropy([x/combined_total for x in M_combined])
        
        # 熵减 = 基线熵 - 组合熵
        delta_H = max(0.0, H_base - H_combined)
        
        # 对数平滑重量（减少大户优势）
        W = sum(m)
        W_smooth = math.log(1 + W)
        
        house_deltas[house_id] = delta_H
        house_weights[house_id] = W_smooth
    
    # 第二步：计算平均熵减（用于相对比较）
    avg_delta_H = sum(house_deltas.values()) / len(house_deltas) if house_deltas else 1.0
    
    # 第三步：混合分配
    # 50% 基础保障（按参与） + 50% 激励（按相对熵减）
    base_pool = total_carbon_credit * 0.5
    incentive_pool = total_carbon_credit * 0.5
    
    credits = {}
    n_households = len(reports_window)
    
    # 基础保障：平均分配
    base_per_house = base_pool / n_households
    
    # 激励部分：按相对熵减分配
    total_relative_score = sum(
        (house_deltas[h] / (avg_delta_H + 0.01)) * house_weights[h] 
        for h in house_deltas
    )
    
    for house_id in house_deltas:
        # 基础部分
        credit = base_per_house
        
        # 激励部分（相对熵减）
        relative_score = (house_deltas[house_id] / (avg_delta_H + 0.01)) * house_weights[house_id]
        ratio = relative_score / (total_relative_score + 0.01)
        incentive = incentive_pool * ratio * alpha
        
        # 上限：不超过平均值的 2.5 倍
        max_credit = (total_carbon_credit / n_households) * 2.5
        credit = min(credit + incentive, max_credit)
        
        credits[house_id] = credit
    
    return credits

def weight_allocation_window(reports_window, total_carbon_credit, alpha=1.0):
    """按重量分配（基线对比）"""
    credits = {}
    total_weight = sum(sum(m) for _, m in reports_window)
    
    if total_weight > 0:
        for house_id, m in reports_window:
            W = sum(m)
            ratio = W / total_weight
            credit = total_carbon_credit * ratio * alpha
            credits[house_id] = credits.get(house_id, 0.0) + credit
    
    return credits

def category_allocation_window(reports_window, weights, total_carbon_credit, alpha=1.0):
    """按类别分配（基线对比）"""
    credits = {}
    total_score = sum(sum(m[k] * weights[k] for k in range(len(m))) for _, m in reports_window)
    
    if total_score > 0:
        for house_id, m in reports_window:
            score = sum(m[k] * weights[k] for k in range(len(m)))
            ratio = score / total_score
            credit = total_carbon_credit * ratio * alpha
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

def calc_fs_utility(credits, alpha_fs=0.5, beta_fs=0.3):
    """
    Fehr-Schmidt 不公平厌恶效用函数
    U_i = x_i - alpha * max(x_j - x_i, 0) - beta * max(x_i - x_j, 0)
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

def run_fpoe_experiment(N=500, K=5, num_days=30, windows_per_day=6, seed=42):
    """
    F-PoER 实验：滑动窗口 + 归一化
    
    Args:
        N: 家庭数
        K: 垃圾类别数
        num_days: 实验天数
        windows_per_day: 每天窗口数（如 6=4 小时/窗）
    """
    random.seed(seed)
    np.random.seed(seed)
    
    print(f"开始 F-PoER 仿真实验...")
    print(f"  家庭数：{N}, 类别数：{K}, 天数：{num_days}, 窗口/天：{windows_per_day}")
    print(f"  总窗口数：{num_days * windows_per_day}")
    
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
    
    results = {
        'carbon_reduction': [],
        'utility_fpoe': [],
        'utility_weight': [],
        'utility_category': [],
        'gini_fpoe': [],
        'gini_weight': [],
        'gini_category': []
    }
    
    total_windows = num_days * windows_per_day
    
    for window_idx in range(total_windows):
        reports_window = []
        total_carbon = 0.0
        
        # 模拟窗口内投放（参与率按窗口调整）
        for hh in households:
            # 窗口参与率 = 日参与率 / 窗口数 + 随机波动
            window_participation = hh.participation_rate / windows_per_day
            window_participation *= random.uniform(0.5, 1.5)  # 随机波动
            window_participation = min(1.0, window_participation)
            
            if random.random() > window_participation:
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
            
            reports_window.append((hh.household_id, sorted_mass))
            total_carbon += carbon_red
        
        if not reports_window:
            continue
        
        # 三种分配机制（窗口级）
        fpoe_cred = fpoe_allocation_window(reports_window, baseline, total_carbon, alpha=1.0)
        weight_cred = weight_allocation_window(reports_window, total_carbon, alpha=1.0)
        cat_weights = [0.8, 1.2, 1.0, 0.9, 0.5]
        category_cred = category_allocation_window(reports_window, cat_weights, total_carbon, alpha=1.0)
        
        results['carbon_reduction'].append(total_carbon)
        results['utility_fpoe'].append(calc_fs_utility(fpoe_cred))
        results['utility_weight'].append(calc_fs_utility(weight_cred))
        results['utility_category'].append(calc_fs_utility(category_cred))
        results['gini_fpoe'].append(gini_coefficient(list(fpoe_cred.values())))
        results['gini_weight'].append(gini_coefficient(list(weight_cred.values())))
        results['gini_category'].append(gini_coefficient(list(category_cred.values())))
        
        if (window_idx + 1) % (windows_per_day * 10) == 0:
            day = (window_idx + 1) // windows_per_day
            print(f"  完成第 {day}/{num_days} 天 (窗口 {window_idx + 1}/{total_windows})")
    
    # 统计摘要
    summary = {
        'avg_carbon_reduction': float(np.mean(results['carbon_reduction'])),
        'std_carbon_reduction': float(np.std(results['carbon_reduction'])),
        'avg_utility_fpoe': float(np.mean(results['utility_fpoe'])),
        'avg_utility_weight': float(np.mean(results['utility_weight'])),
        'avg_utility_category': float(np.mean(results['utility_category'])),
        'avg_gini_fpoe': float(np.mean(results['gini_fpoe'])),
        'avg_gini_weight': float(np.mean(results['gini_weight'])),
        'avg_gini_category': float(np.mean(results['gini_category'])),
        'utility_gain_fpoe_vs_weight': float((np.mean(results['utility_fpoe']) - np.mean(results['utility_weight'])) / (abs(np.mean(results['utility_weight'])) + 0.01) * 100),
        'fairness_improvement_fpoe_vs_weight': float((np.mean(results['gini_weight']) - np.mean(results['gini_fpoe'])) / (np.mean(results['gini_weight']) + 0.01) * 100),
        'gini_reduction_vs_original_poer': float((0.8508 - np.mean(results['gini_fpoe'])) / 0.8508 * 100)  # 对比原始 PoER
    }
    
    print("\n" + "=" * 70)
    print("F-PoER 实验结果摘要")
    print("=" * 70)
    for k, v in summary.items():
        print(f"  {k}: {v:.4f}")
    
    return results, summary

if __name__ == '__main__':
    results, summary = run_fpoe_experiment(N=500, K=5, num_days=30, windows_per_day=6, seed=42)
    
    # 保存结果
    output_dir = Path('/home/admin/.openclaw/workspace/poer_experiments/outputs')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / 'results_fpoe.json', 'w', encoding='utf-8') as f:
        json.dump({'results': results, 'summary': summary}, f, indent=2)
    
    print(f"\n结果已保存至：{output_dir / 'results_fpoe.json'}")
