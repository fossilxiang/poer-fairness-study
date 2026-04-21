#!/usr/bin/env python3
"""
PoER: Proof of Entropy Reduction - 垃圾分类碳积分分配算法

实现论文中的核心算法，支持仿真实验和对比分析。
"""

import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, field
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from scipy import stats
import pandas as pd
from datetime import datetime

# ============== 数据类定义 ==============

@dataclass
class Household:
    """家庭节点"""
    household_id: int
    sorting_accuracy: float  # 分类精度 (0-1)
    waste_generation: float  # 日均垃圾产生量 (kg)
    participation_rate: float  # 参与率 (0-1)
    
@dataclass
class WasteComposition:
    """垃圾组分"""
    name: str
    proportion: float  # 质量分数
    carbon_factor_mix: float  # 混合处置碳排放因子 (kg CO2e/kg)
    carbon_factor_sorted: float  # 分类处置碳排放因子 (kg CO2e/kg)
    
@dataclass
class SlotResult:
    """单轮实验结果"""
    slot: int
    total_entropy_reduction: float
    total_carbon_reduction: float
    total_credits: float
    household_utilities: Dict[int, float]
    gini_coefficient: float  # 公平性指标

# ============== 核心算法 ==============

def compute_entropy(prob_vec: np.ndarray) -> float:
    """计算信息熵（香农熵）"""
    prob_vec = np.asarray(prob_vec)
    prob_vec = prob_vec[prob_vec > 0]
    if len(prob_vec) == 0:
        return 0.0
    return -np.sum(prob_vec * np.log2(prob_vec))

def generate_confusion_matrix(K: int, accuracy: float, rng: np.random.Generator) -> np.ndarray:
    """
    生成分类混淆矩阵
    
    Args:
        K: 垃圾类别数
        accuracy: 分类精度 (对角线元素平均值)
        rng: 随机数生成器
    
    Returns:
        K×K 混淆矩阵，a[jk] = P(将 j 类投放到 k 类桶)
    """
    A = np.eye(K) * accuracy
    # 非对角线元素（错误分类）
    error_prob = (1 - accuracy) / (K - 1)
    for j in range(K):
        for k in range(K):
            if j != k:
                A[j, k] = error_prob
    # 归一化确保每行和为 1
    A = A / A.sum(axis=1, keepdims=True)
    return A

def simulate_household_sorting(
    household: Household,
    waste_composition: np.ndarray,
    confusion_matrix: np.ndarray,
    K: int
) -> Tuple[np.ndarray, float]:
    """
    模拟家庭分类行为
    
    Returns:
        sorted_mass: 分类后各桶质量向量
        entropy_reduction: 局部熵减量
    """
    # 分类前混合熵
    H_before = compute_entropy(waste_composition)
    
    # 分类后分布：y = x · A
    sorted_composition = waste_composition @ confusion_matrix
    
    # 分类后熵
    H_after = compute_entropy(sorted_composition)
    
    # 熵减
    entropy_reduction = max(0, H_before - H_after)
    
    # 各桶质量
    total_mass = household.waste_generation
    sorted_mass = sorted_composition * total_mass
    
    return sorted_mass, entropy_reduction

def compute_carbon_reduction(
    waste_composition: np.ndarray,
    sorted_composition: np.ndarray,
    carbon_factors_mix: np.ndarray,
    carbon_factors_sorted: np.ndarray,
    total_mass: float
) -> float:
    """
    计算碳减排量
    
    Returns:
        carbon_reduction: 碳减排量 (kg CO2e)
    """
    # 混合处置碳排放
    carbon_mix = np.sum(waste_composition * carbon_factors_mix)
    
    # 分类处置碳排放
    carbon_sorted = np.sum(sorted_composition * carbon_factors_sorted)
    
    # 碳减排量
    carbon_reduction = (carbon_mix - carbon_sorted) * total_mass
    
    return max(0, carbon_reduction)

def poer_credit_allocation(
    household_reports: List[Tuple[int, np.ndarray]],
    community_baseline: np.ndarray,
    alpha: float = 100.0
) -> Dict[int, float]:
    """
    PoER 积分分配算法
    
    Args:
        household_reports: [(house_id, mass_vector), ...]
        community_baseline: 社区基准质量分布
        alpha: 积分转换系数
    
    Returns:
        credits: {house_id: total_credit}
    """
    K = len(community_baseline)
    M_community = community_baseline.copy()
    credits = {}
    
    for house_id, m in household_reports:
        # 1. 记录先验分布与熵
        prior_total = np.sum(M_community)
        if prior_total == 0:
            H_prior = compute_entropy(community_baseline)
        else:
            prior_frac = M_community / prior_total
            H_prior = compute_entropy(prior_frac)
        
        # 2. 更新社区总质量
        M_community = M_community + m
        post_total = np.sum(M_community)
        post_frac = M_community / post_total
        H_post = compute_entropy(post_frac)
        
        # 3. 计算边际熵减
        delta_H = max(0.0, H_prior - H_post)
        
        # 4. 家庭当日投放总质量
        W = np.sum(m)
        
        # 5. 分配积分
        credit = alpha * delta_H * W
        
        if house_id not in credits:
            credits[house_id] = 0.0
        credits[house_id] += credit
    
    return credits

def weight_based_allocation(
    household_reports: List[Tuple[int, np.ndarray]],
    beta: float = 10.0
) -> Dict[int, float]:
    """按重量分配积分（基线方法）"""
    credits = {}
    for house_id, m in household_reports:
        W = np.sum(m)
        credit = beta * W
        if house_id not in credits:
            credits[house_id] = 0.0
        credits[house_id] += credit
    return credits

def category_based_allocation(
    household_reports: List[Tuple[int, np.ndarray]],
    category_weights: np.ndarray,
    gamma: float = 10.0
) -> Dict[int, float]:
    """按类别分配积分（基线方法）"""
    credits = {}
    for house_id, m in household_reports:
        # 可回收物权重更高
        credit = gamma * np.sum(m * category_weights)
        if house_id not in credits:
            credits[house_id] = 0.0
        credits[house_id] += credit
    return credits

def compute_gini_coefficient(values: np.ndarray) -> float:
    """计算基尼系数（公平性指标）"""
    if len(values) == 0 or np.sum(values) == 0:
        return 0.0
    sorted_values = np.sort(values)
    n = len(sorted_values)
    cumsum = np.cumsum(sorted_values)
    gini = (2 * np.sum((np.arange(1, n + 1) * sorted_values))) / (n * np.sum(sorted_values)) - (n + 1) / n
    return max(0, min(1, gini))

def compute_utility(
    credit: float,
    carbon_reduction: float,
    sorting_cost: float,
    w1: float = 0.5,
    w2: float = 0.3,
    w3: float = 0.2
) -> float:
    """
    计算家庭效用函数
    
    U = w1 * credit - w2 * sorting_cost + w3 * carbon_reduction
    """
    return w1 * credit - w2 * sorting_cost + w3 * carbon_reduction

# ============== 实验运行器 ==============

class PoERExperiment:
    """PoER 仿真实验器"""
    
    def __init__(self, config: dict, seed: int = 42):
        self.config = config
        self.rng = np.random.default_rng(seed)
        self.K = config.get('num_categories', 5)
        self.N = config.get('num_households', 500)
        self.num_slots = config.get('num_slots', 30)
        
        # 初始化垃圾类别
        self.category_names = config.get('category_names', 
            ['厨余', '可回收', '有害', '玻璃', '其他'])
        
        # 碳排放因子（kg CO2e/kg）
        self.carbon_factors_mix = np.array(config.get('carbon_factors_mix', 
            [0.5, 0.3, 0.8, 0.2, 0.6]))
        self.carbon_factors_sorted = np.array(config.get('carbon_factors_sorted',
            [0.1, -0.2, 0.3, 0.05, 0.5]))  # 可回收为负（碳汇）
        
        # 基准垃圾组分
        self.baseline_composition = np.array(config.get('baseline_composition',
            [0.4, 0.25, 0.05, 0.1, 0.2]))
        
        # 初始化家庭
        self.households = self._initialize_households()
        
        # 结果存储
        self.results = {
            'poer': [],
            'weight': [],
            'category': []
        }
        
    def _initialize_households(self) -> List[Household]:
        """初始化 heterogeneous 家庭群体"""
        households = []
        for i in range(self.N):
            # 分类精度服从正态分布（均值 0.7，标准差 0.15）
            accuracy = np.clip(self.rng.normal(0.7, 0.15), 0.3, 0.95)
            # 垃圾产生量服从对数正态分布
            waste_gen = np.clip(self.rng.lognormal(1.5, 0.3), 0.5, 5.0)
            # 参与率服从 Beta 分布
            participation = self.rng.beta(2, 2)
            
            households.append(Household(
                household_id=i,
                sorting_accuracy=accuracy,
                waste_generation=waste_gen,
                participation_rate=participation
            ))
        return households
    
    def run_slot(self, slot: int) -> SlotResult:
        """运行单轮仿真"""
        # 1. 生成家庭上报数据
        household_reports = []
        total_entropy_reduction = 0.0
        total_carbon_reduction = 0.0
        
        for hh in self.households:
            if self.rng.random() > hh.participation_rate:
                continue  # 不参与
            
            # 生成真实垃圾组分（有随机波动）
            waste_comp = self.baseline_composition + self.rng.normal(0, 0.05, self.K)
            waste_comp = np.clip(waste_comp, 0.01, 1.0)
            waste_comp = waste_comp / waste_comp.sum()
            
            # 生成混淆矩阵
            confusion_mat = generate_confusion_matrix(
                self.K, hh.sorting_accuracy, self.rng
            )
            
            # 模拟分类
            sorted_mass, entropy_red = simulate_household_sorting(
                hh, waste_comp, confusion_mat, self.K
            )
            
            # 计算碳减排
            carbon_red = compute_carbon_reduction(
                waste_comp,
                sorted_mass / hh.waste_generation,
                self.carbon_factors_mix,
                self.carbon_factors_sorted,
                hh.waste_generation
            )
            
            household_reports.append((hh.household_id, sorted_mass))
            total_entropy_reduction += entropy_red
            total_carbon_reduction += carbon_red
        
        # 2. 三种积分分配机制
        poer_credits = poer_credit_allocation(
            household_reports,
            self.baseline_composition * 100,  # 基准质量
            alpha=100.0
        )
        
        weight_credits = weight_based_allocation(
            household_reports,
            beta=10.0
        )
        
        category_weights = np.array([0.8, 1.2, 1.0, 0.9, 0.5])  # 可回收权重高
        category_credits = category_based_allocation(
            household_reports,
            category_weights,
            gamma=10.0
        )
        
        # 3. 计算效用和公平性
        poer_utilities = []
        weight_utilities = []
        category_utilities = []
        
        for hh in self.households:
            if hh.household_id not in [r[0] for r in household_reports]:
                continue
            
            # 找到该家庭的上报
            for house_id, m in household_reports:
                if house_id == hh.household_id:
                    # 分类成本（时间精力）
                    sorting_cost = hh.waste_generation * (1 + 2 * (1 - hh.sorting_accuracy))
                    
                    u_poer = compute_utility(
                        poer_credits.get(hh.household_id, 0),
                        compute_carbon_reduction(
                            self.baseline_composition,
                            m / hh.waste_generation,
                            self.carbon_factors_mix,
                            self.carbon_factors_sorted,
                            hh.waste_generation
                        ),
                        sorting_cost
                    )
                    
                    u_weight = compute_utility(
                        weight_credits.get(hh.household_id, 0),
                        compute_carbon_reduction(
                            self.baseline_composition,
                            m / hh.waste_generation,
                            self.carbon_factors_mix,
                            self.carbon_factors_sorted,
                            hh.waste_generation
                        ),
                        sorting_cost
                    )
                    
                    u_category = compute_utility(
                        category_credits.get(hh.household_id, 0),
                        compute_carbon_reduction(
                            self.baseline_composition,
                            m / hh.waste_generation,
                            self.carbon_factors_mix,
                            self.carbon_factors_sorted,
                            hh.waste_generation
                        ),
                        sorting_cost
                    )
                    
                    poer_utilities.append(u_poer)
                    weight_utilities.append(u_weight)
                    category_utilities.append(u_category)
                    break
        
        # 4. 计算基尼系数
        poer_gini = compute_gini_coefficient(np.array(list(poer_credits.values())))
        weight_gini = compute_gini_coefficient(np.array(list(weight_credits.values())))
        category_gini = compute_gini_coefficient(np.array(list(category_credits.values())))
        
        return SlotResult(
            slot=slot,
            total_entropy_reduction=total_entropy_reduction,
            total_carbon_reduction=total_carbon_reduction,
            total_credits=sum(poer_credits.values()),
            household_utilities={
                'poer': np.mean(poer_utilities) if poer_utilities else 0,
                'weight': np.mean(weight_utilities) if weight_utilities else 0,
                'category': np.mean(category_utilities) if category_utilities else 0
            },
            gini_coefficient={
                'poer': poer_gini,
                'weight': weight_gini,
                'category': category_gini
            }
        )
    
    def run_experiment(self) -> Dict:
        """运行完整实验"""
        print(f"开始 PoER 仿真实验...")
        print(f"  家庭数：{self.N}")
        print(f"  垃圾类别：{self.K}")
        print(f"  仿真轮数：{self.num_slots}")
        
        all_results = {
            'entropy_reduction': [],
            'carbon_reduction': [],
            'utilities': {'poer': [], 'weight': [], 'category': []},
            'gini': {'poer': [], 'weight': [], 'category': []},
            'slots': []
        }
        
        for slot in range(self.num_slots):
            result = self.run_slot(slot)
            
            all_results['entropy_reduction'].append(result.total_entropy_reduction)
            all_results['carbon_reduction'].append(result.total_carbon_reduction)
            all_results['utilities']['poer'].append(result.household_utilities['poer'])
            all_results['utilities']['weight'].append(result.household_utilities['weight'])
            all_results['utilities']['category'].append(result.household_utilities['category'])
            all_results['gini']['poer'].append(result.gini_coefficient['poer'])
            all_results['gini']['weight'].append(result.gini_coefficient['weight'])
            all_results['gini']['category'].append(result.gini_coefficient['category'])
            all_results['slots'].append(slot)
            
            if (slot + 1) % 10 == 0:
                print(f"  完成第 {slot + 1}/{self.num_slots} 轮")
        
        print("实验完成！")
        return all_results

def generate_figures(results: Dict, output_dir: Path):
    """生成论文图表"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 设置风格
    sns.set_style("whitegrid")
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 13
    
    # 图 1: 碳减排量对比
    fig, ax = plt.subplots(figsize=(10, 6))
    slots = results['slots']
    ax.plot(slots, results['carbon_reduction'], 'g-', linewidth=2, 
            label='Carbon Reduction', marker='o', markersize=4)
    ax.set_xlabel('Time Slot (day)')
    ax.set_ylabel('Carbon Reduction (kg CO₂e)')
    ax.set_title('Daily Carbon Reduction Over Time')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'carbon_reduction_over_time.pdf', dpi=300)
    plt.savefig(output_dir / 'carbon_reduction_over_time.png', dpi=150)
    plt.close()
    
    # 图 2: 三种机制效用对比
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(slots, results['utilities']['poer'], 'b-', linewidth=2, 
            label='PoER (Ours)', marker='o', markersize=4)
    ax.plot(slots, results['utilities']['weight'], 'r--', linewidth=2, 
            label='Weight-based', marker='s', markersize=4)
    ax.plot(slots, results['utilities']['category'], 'g-.', linewidth=2, 
            label='Category-based', marker='^', markersize=4)
    ax.set_xlabel('Time Slot (day)')
    ax.set_ylabel('Average Household Utility')
    ax.set_title('Utility Comparison of Different Incentive Mechanisms')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'utility_comparison.pdf', dpi=300)
    plt.savefig(output_dir / 'utility_comparison.png', dpi=150)
    plt.close()
    
    # 图 3: 基尼系数（公平性）对比
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(slots, results['gini']['poer'], 'b-', linewidth=2, 
            label='PoER (Ours)', marker='o', markersize=4)
    ax.plot(slots, results['gini']['weight'], 'r--', linewidth=2, 
            label='Weight-based', marker='s', markersize=4)
    ax.plot(slots, results['gini']['category'], 'g-.', linewidth=2, 
            label='Category-based', marker='^', markersize=4)
    ax.set_xlabel('Time Slot (day)')
    ax.set_ylabel('Gini Coefficient')
    ax.set_title('Fairness Comparison (Lower is Better)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'fairness_comparison.pdf', dpi=300)
    plt.savefig(output_dir / 'fairness_comparison.png', dpi=150)
    plt.close()
    
    # 图 4: 熵减量分布
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(results['entropy_reduction'], bins=20, color='purple', 
            alpha=0.7, edgecolor='black')
    ax.set_xlabel('Entropy Reduction (bits)')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of Daily Entropy Reduction')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'entropy_distribution.pdf', dpi=300)
    plt.savefig(output_dir / 'entropy_distribution.png', dpi=150)
    plt.close()
    
    # 图 5: 效用对比箱线图
    fig, ax = plt.subplots(figsize=(10, 6))
    utility_data = [
        results['utilities']['poer'],
        results['utilities']['weight'],
        results['utilities']['category']
    ]
    bp = ax.boxplot(utility_data, labels=['PoER', 'Weight', 'Category'],
                    patch_artist=True)
    colors = ['blue', 'red', 'green']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.5)
    ax.set_ylabel('Household Utility')
    ax.set_title('Utility Distribution Comparison')
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_dir / 'utility_boxplot.pdf', dpi=300)
    plt.savefig(output_dir / 'utility_boxplot.png', dpi=150)
    plt.close()
    
    # 图 6: 热图 - 分类精度 vs 效用增益
    fig, ax = plt.subplots(figsize=(10, 8))
    accuracies = np.linspace(0.3, 0.95, 20)
    utilities = []
    for acc in accuracies:
        # 简化的效用计算
        utility = acc * 50 - (1 - acc) * 20 + acc * 30
        utilities.append(utility)
    
    im = ax.imshow(np.array(utilities).reshape(-1, 1), aspect='auto', 
                   cmap='YlOrRd', extent=[0, 1, accuracies.min(), accuracies.max()])
    ax.set_xlabel('Participation Rate')
    ax.set_ylabel('Sorting Accuracy')
    ax.set_title('Utility Heatmap vs Sorting Accuracy')
    plt.colorbar(im, label='Utility')
    plt.tight_layout()
    plt.savefig(output_dir / 'utility_heatmap.pdf', dpi=300)
    plt.savefig(output_dir / 'utility_heatmap.png', dpi=150)
    plt.close()
    
    print(f"图表已保存至：{output_dir}")

def run_sensitivity_analysis(output_dir: Path):
    """敏感性分析"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    sns.set_style("whitegrid")
    
    # 分析不同家庭数目的影响
    N_values = [100, 200, 500, 1000, 2000]
    carbon_results = []
    
    for N in N_values:
        config = {
            'num_households': N,
            'num_categories': 5,
            'num_slots': 10
        }
        exp = PoERExperiment(config, seed=42)
        results = exp.run_experiment()
        carbon_results.append(np.mean(results['carbon_reduction']))
    
    # 绘制敏感性分析图
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(N_values, carbon_results, 'bo-', linewidth=2, markersize=8)
    ax.set_xlabel('Number of Households')
    ax.set_ylabel('Average Carbon Reduction (kg CO₂e)')
    ax.set_title('Sensitivity Analysis: System Scale')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'sensitivity_scale.pdf', dpi=300)
    plt.savefig(output_dir / 'sensitivity_scale.png', dpi=150)
    plt.close()
    
    print(f"敏感性分析图已保存至：{output_dir}")

if __name__ == '__main__':
    # 配置
    config = {
        'num_households': 500,
        'num_categories': 5,
        'num_slots': 30,
        'category_names': ['厨余', '可回收', '有害', '玻璃', '其他'],
        'carbon_factors_mix': [0.5, 0.3, 0.8, 0.2, 0.6],
        'carbon_factors_sorted': [0.1, -0.2, 0.3, 0.05, 0.5],
        'baseline_composition': [0.4, 0.25, 0.05, 0.1, 0.2]
    }
    
    # 输出目录
    output_dir = Path('/home/admin/.openclaw/workspace/poer_experiments/outputs')
    
    # 运行实验
    exp = PoERExperiment(config, seed=42)
    results = exp.run_experiment()
    
    # 生成图表
    generate_figures(results, output_dir / 'figures')
    
    # 敏感性分析
    run_sensitivity_analysis(output_dir / 'sensitivity')
    
    # 保存结果
    import json
    results_json = {
        'entropy_reduction': results['entropy_reduction'],
        'carbon_reduction': results['carbon_reduction'],
        'utilities': results['utilities'],
        'gini': results['gini'],
        'summary': {
            'avg_carbon_reduction': float(np.mean(results['carbon_reduction'])),
            'std_carbon_reduction': float(np.std(results['carbon_reduction'])),
            'avg_utility_poer': float(np.mean(results['utilities']['poer'])),
            'avg_utility_weight': float(np.mean(results['utilities']['weight'])),
            'avg_utility_category': float(np.mean(results['utilities']['category'])),
            'avg_gini_poer': float(np.mean(results['gini']['poer'])),
            'avg_gini_weight': float(np.mean(results['gini']['weight'])),
            'avg_gini_category': float(np.mean(results['gini']['category']))
        }
    }
    
    with open(output_dir / 'results.json', 'w', encoding='utf-8') as f:
        json.dump(results_json, f, indent=2, ensure_ascii=False)
    
    print(f"\n实验结果摘要:")
    print(f"  平均碳减排：{results_json['summary']['avg_carbon_reduction']:.2f} kg CO₂e/天")
    print(f"  PoER 平均效用：{results_json['summary']['avg_utility_poer']:.2f}")
    print(f"  按重量平均效用：{results_json['summary']['avg_utility_weight']:.2f}")
    print(f"  按类别平均效用：{results_json['summary']['avg_utility_category']:.2f}")
    print(f"  PoER 基尼系数：{results_json['summary']['avg_gini_poer']:.3f}")
    print(f"  按重量基尼系数：{results_json['summary']['avg_gini_weight']:.3f}")
    print(f"  按类别基尼系数：{results_json['summary']['avg_gini_category']:.3f}")
