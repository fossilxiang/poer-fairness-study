#!/usr/bin/env python3
"""
Ablation Study for F-PoER
消融实验：评估 F-PoER 各组件的贡献

生成 Table 2 数据：
- 时间窗口效果
- 相对熵减效果
- 混合分配效果
- 对数质量因子效果
- 上限效果
- 超参数敏感性
"""

import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Tuple
import math
import random

# 导入基础算法
import sys
sys.path.insert(0, str(Path(__file__).parent))
from poer_fpoe_experiment import Household, compute_entropy, generate_confusion_matrix

class AblationExperiment:
    def __init__(self, seed=42):
        self.rng = np.random.default_rng(seed)
        self.N_households = 500
        self.K_categories = 5
        self.days = 30
        
        # 基础参数
        self.p_base = np.array([0.40, 0.25, 0.05, 0.10, 0.20])
        self.M_base = self.p_base * 1000  # 基准质量
        
        # 生成用户
        self.households = self._generate_households()
        
    def _generate_households(self):
        """生成 500 个用户"""
        households = []
        for i in range(self.N_households):
            # 分类准确率：正态分布，均值 0.7，标准差 0.15
            accuracy = float(self.rng.normal(0.70, 0.15))
            accuracy = np.clip(accuracy, 0.3, 0.95)
            
            # 垃圾产生量：对数正态分布
            waste = float(self.rng.lognormal(1.5, 0.3))
            
            # 参与率：Beta(2,2)
            participation = float(self.rng.beta(2, 2))
            
            households.append(Household(
                household_id=i,
                sorting_accuracy=accuracy,
                waste_generation=waste,
                participation_rate=participation
            ))
        return households
    
    def _simulate_day(self, day_idx, config):
        """模拟一天的投放"""
        reports = []
        
        # 决定哪些用户参与
        participating = []
        for h in self.households:
            if self.rng.random() < h.participation_rate:
                participating.append(h)
        
        # 随机顺序
        self.rng.shuffle(participating)
        
        for h in participating:
            # 生成投放质量向量
            m = self._generate_mass_vector(h)
            reports.append((h.household_id, m))
        
        return reports
    
    def _generate_mass_vector(self, household: Household):
        """生成用户投放的质量向量"""
        # 真实组分
        true_mass = household.waste_generation * self.p_base
        
        # 混淆矩阵
        A = generate_confusion_matrix(self.K_categories, household.sorting_accuracy, self.rng)
        
        # 观测组分
        observed_mass = [0.0] * self.K_categories
        for j in range(self.K_categories):
            for k in range(self.K_categories):
                observed_mass[k] += A[j][k] * true_mass[j]
        
        return observed_mass
    
    def _compute_poer_credits(self, reports, total_credit):
        """原始 PoER：顺序分配"""
        M_current = list(self.M_base)
        credits = {}
        
        for house_id, m in reports:
            # 计算当前熵
            total = sum(M_current)
            H_prior = compute_entropy([x/total for x in M_current])
            
            # 添加该户投放
            M_combined = [M_current[k] + m[k] for k in range(self.K_categories)]
            total_combined = sum(M_combined)
            H_combined = compute_entropy([x/total_combined for x in M_combined])
            
            # 边际熵减
            delta_H = max(0.0, H_prior - H_combined)
            credits[house_id] = delta_H
            
            # 更新累积
            M_current = M_combined
        
        # 归一化到总积分池
        total = sum(credits.values())
        if total > 0:
            scale = total_credit / total
            for k in credits:
                credits[k] *= scale
        
        return credits
    
    def _compute_fpoe_credits(self, reports, total_credit, config):
        """
        F-PoER：可配置版本
        
        config 包含：
        - use_windows: 是否使用时间窗口
        - use_relative: 是否使用相对熵减
        - use_hybrid: 是否使用混合分配
        - use_log_mass: 是否使用对数质量因子
        - use_cap: 是否使用上限
        - window_count: 窗口数量
        - hybrid_ratio: 混合比例 (baseline:performance)
        - cap_multiplier: 上限倍数
        """
        K = self.K_categories
        
        # 默认配置
        use_windows = config.get('use_windows', False)
        use_relative = config.get('use_relative', False)
        use_hybrid = config.get('use_hybrid', False)
        use_log_mass = config.get('use_log_mass', False)
        use_cap = config.get('use_cap', False)
        window_count = config.get('window_count', 6)
        hybrid_ratio = config.get('hybrid_ratio', 0.5)
        cap_multiplier = config.get('cap_multiplier', 2.5)
        
        if not use_windows:
            # 单窗口（原始 F-PoER）
            credits = self._compute_single_window(reports, total_credit, config)
        else:
            # 多时间窗口
            credits = self._compute_multi_window(reports, total_credit, config)
        
        # 应用上限
        if use_cap:
            avg_credit = total_credit / len(reports) if reports else 0
            max_credit = cap_multiplier * avg_credit
            for house_id in credits:
                credits[house_id] = min(credits[house_id], max_credit)
        
        return credits
    
    def _compute_single_window(self, reports, total_credit, config):
        """单窗口 F-PoER"""
        K = self.K_categories
        use_relative = config.get('use_relative', False)
        use_hybrid = config.get('use_hybrid', False)
        use_log_mass = config.get('use_log_mass', False)
        hybrid_ratio = config.get('hybrid_ratio', 0.5)
        
        if not reports:
            return {}
        
        # 计算每户独立熵减
        house_deltas = {}
        house_weights = {}
        
        for house_id, m in reports:
            M_combined = [self.M_base[k] + m[k] for k in range(K)]
            base_total = sum(self.M_base)
            combined_total = sum(M_combined)
            
            H_base = compute_entropy([x/base_total for x in self.M_base]) if base_total > 0 else 0
            H_combined = compute_entropy([x/combined_total for x in M_combined]) if combined_total > 0 else 0
            
            delta_H = max(0.0, H_base - H_combined)
            W = sum(m)
            W_smooth = math.log(1 + W) if use_log_mass else W
            
            house_deltas[house_id] = delta_H
            house_weights[house_id] = W_smooth
        
        # 相对熵减
        if use_relative:
            avg_delta = sum(house_deltas.values()) / len(house_deltas) if house_deltas else 1.0
            for house_id in house_deltas:
                house_deltas[house_id] /= (avg_delta + 0.01)
        
        # 混合分配
        if use_hybrid:
            base_pool = total_credit * hybrid_ratio
            perf_pool = total_credit * (1 - hybrid_ratio)
            
            credits = {}
            # 基础保障
            base_per_house = base_pool / len(reports) if reports else 0
            
            # 绩效分配
            total_score = sum(house_deltas[h] * house_weights[h] for h in house_deltas)
            
            for house_id in house_deltas:
                perf_share = (house_deltas[house_id] * house_weights[house_id] / total_score) if total_score > 0 else 0
                credits[house_id] = base_per_house + perf_pool * perf_share
            
            return credits
        else:
            # 纯绩效 - 修复：确保正确归一化
            total_score = sum(house_deltas[h] * house_weights[h] for h in house_deltas)
            credits = {}
            if total_score > 0:
                for house_id in house_deltas:
                    share = (house_deltas[house_id] * house_weights[house_id]) / total_score
                    credits[house_id] = total_credit * share
            else:
                # 如果所有熵减都是 0，平均分配
                for house_id in house_deltas:
                    credits[house_id] = total_credit / len(house_deltas)
            return credits
    
    def _compute_multi_window(self, reports, total_credit, config):
        """多时间窗口 F-PoER"""
        window_count = config.get('window_count', 6)
        credit_per_window = total_credit / window_count
        
        # 随机分配到窗口
        window_assignments = {i: [] for i in range(window_count)}
        for report in reports:
            window_idx = self.rng.integers(0, window_count)
            window_assignments[window_idx].append(report)
        
        # 合并各窗口积分
        all_credits = {}
        for window_idx, window_reports in window_assignments.items():
            if not window_reports:
                continue
            
            # 为每个窗口重置基线
            old_base = self.M_base
            self.M_base = [x / window_count for x in self.M_base]  # 缩小基线
            
            window_credits = self._compute_single_window(window_reports, credit_per_window, config)
            
            self.M_base = old_base
            
            for house_id, credit in window_credits.items():
                all_credits[house_id] = all_credits.get(house_id, 0) + credit
        
        return all_credits
    
    def _compute_gini(self, credits):
        """计算基尼系数"""
        values = list(credits.values())
        if not values or sum(values) == 0:
            return 0.0
        
        n = len(values)
        values_sorted = sorted(values)
        
        cumsum = np.cumsum(values_sorted)
        return (2 * sum((i + 1) * v for i, v in enumerate(values_sorted)) - (n + 1) * cumsum[-1]) / (n * cumsum[-1])
    
    def _compute_top_share(self, credits, top_pct=0.1):
        """计算前 top% 的份额"""
        values = sorted(credits.values(), reverse=True)
        total = sum(values)
        if total == 0:
            return 0.0
        
        top_n = max(1, int(len(values) * top_pct))
        return sum(values[:top_n]) / total
    
    def _compute_fs_utility(self, credits, alpha=0.5, beta=0.3):
        """计算 Fehr-Schmidt 效用（人口均值）"""
        values = list(credits.values())
        n = len(values)
        if n == 0:
            return 0.0
        
        utilities = []
        for i, c_i in enumerate(values):
            envy = sum(max(c_j - c_i, 0) for j, c_j in enumerate(values) if j != i) / (n - 1)
            guilt = sum(max(c_i - c_j, 0) for j, c_j in enumerate(values) if j != i) / (n - 1)
            u_i = c_i - alpha * envy - beta * guilt
            utilities.append(u_i)
        
        return np.mean(utilities)
    
    def run_ablation(self, n_days=30, total_credit_per_day=1000):
        """运行消融实验"""
        configs = [
            {'name': 'PoER (baseline)', 'use_windows': False, 'use_relative': False, 'use_hybrid': False, 'use_log_mass': False, 'use_cap': False, 'use_poer': True},
            {'name': '+ Temporal windows (W=6)', 'use_windows': True, 'window_count': 6, 'use_relative': False, 'use_hybrid': False, 'use_log_mass': False, 'use_cap': False, 'use_poer': False},
            {'name': '+ Relative ΔH', 'use_windows': True, 'window_count': 6, 'use_relative': True, 'use_hybrid': False, 'use_log_mass': False, 'use_cap': False, 'use_poer': False},
            {'name': '+ Hybrid split (50:50)', 'use_windows': True, 'window_count': 6, 'use_relative': True, 'use_hybrid': True, 'hybrid_ratio': 0.5, 'use_log_mass': False, 'use_cap': False, 'use_poer': False},
            {'name': '+ Logarithmic mass factor', 'use_windows': True, 'window_count': 6, 'use_relative': True, 'use_hybrid': True, 'hybrid_ratio': 0.5, 'use_log_mass': True, 'use_cap': False, 'use_poer': False},
            {'name': '+ Cap (2.5×)', 'use_windows': True, 'window_count': 6, 'use_relative': True, 'use_hybrid': True, 'hybrid_ratio': 0.5, 'use_log_mass': True, 'use_cap': True, 'cap_multiplier': 2.5, 'use_poer': False},
            
            # 混合比例敏感性
            {'name': '70:30 baseline:performance', 'use_windows': True, 'window_count': 6, 'use_relative': True, 'use_hybrid': True, 'hybrid_ratio': 0.7, 'use_log_mass': True, 'use_cap': True, 'cap_multiplier': 2.5, 'use_poer': False},
            {'name': '30:70 baseline:performance', 'use_windows': True, 'window_count': 6, 'use_relative': True, 'use_hybrid': True, 'hybrid_ratio': 0.3, 'use_log_mass': True, 'use_cap': True, 'cap_multiplier': 2.5, 'use_poer': False},
            
            # 窗口数量敏感性
            {'name': 'W=3 (8-hour windows)', 'use_windows': True, 'window_count': 3, 'use_relative': True, 'use_hybrid': True, 'hybrid_ratio': 0.5, 'use_log_mass': True, 'use_cap': True, 'cap_multiplier': 2.5, 'use_poer': False},
            {'name': 'W=12 (2-hour windows)', 'use_windows': True, 'window_count': 12, 'use_relative': True, 'use_hybrid': True, 'hybrid_ratio': 0.5, 'use_log_mass': True, 'use_cap': True, 'cap_multiplier': 2.5, 'use_poer': False},
        ]
        
        results = []
        
        for config in configs:
            print(f"Running: {config['name']}...")
            
            all_credits = {}
            total_carbon = 0
            
            for day in range(n_days):
                reports = self._simulate_day(day, config)
                if not reports:
                    continue
                
                # 使用 PoER 或 F-PoER
                if config.get('use_poer', False):
                    credits = self._compute_poer_credits(reports, total_credit_per_day)
                else:
                    credits = self._compute_fpoe_credits(reports, total_credit_per_day, config)
                
                for house_id, credit in credits.items():
                    all_credits[house_id] = all_credits.get(house_id, 0) + credit
                
                # 估算碳减排
                total_carbon += total_credit_per_day  # 简化：假设 1 credit = 1 kg CO2
            
            gini = self._compute_gini(all_credits)
            top_share = self._compute_top_share(all_credits)
            fs_utility = self._compute_fs_utility(all_credits)
            
            results.append({
                'name': config['name'],
                'gini': round(gini, 4),
                'top_10_share': f"{top_share*100:.1f}%",
                'carbon_kg_day': round(total_carbon / n_days, 1),
                'fs_utility': round(fs_utility, 2)
            })
            
            print(f"  Gini: {gini:.4f}, Top 10%: {top_share*100:.1f}%, FS Utility: {fs_utility:.2f}")
        
        return results
    
    def run_robustness(self, n_seeds=100, n_days=30):
        """鲁棒性分析：多种子"""
        poer_ginis = []
        fpoe_ginis = []
        poer_carbon = []
        fpoe_carbon = []
        
        poer_config = {'use_windows': False, 'use_relative': False, 'use_hybrid': False, 'use_log_mass': False, 'use_cap': False}
        fpoe_config = {'use_windows': True, 'window_count': 6, 'use_relative': True, 'use_hybrid': True, 'hybrid_ratio': 0.5, 'use_log_mass': True, 'use_cap': True, 'cap_multiplier': 2.5}
        
        for seed in range(n_seeds):
            if seed % 10 == 0:
                print(f"  Seed {seed}/{n_seeds}...")
            
            self.rng = np.random.default_rng(seed)
            self.households = self._generate_households()
            
            for config, gini_list, carbon_list in [
                (poer_config, poer_ginis, poer_carbon),
                (fpoe_config, fpoe_ginis, fpoe_carbon)
            ]:
                all_credits = {}
                total_carbon = 0
                
                for day in range(n_days):
                    reports = self._simulate_day(day, config)
                    if not reports:
                        continue
                    
                    if config['use_windows']:
                        credits = self._compute_fpoe_credits(reports, 1000, config)
                    else:
                        credits = self._compute_poer_credits(reports, 1000)
                    
                    for house_id, credit in credits.items():
                        all_credits[house_id] = all_credits.get(house_id, 0) + credit
                    
                    total_carbon += 1000
                
                gini = self._compute_gini(all_credits)
                gini_list.append(gini)
                carbon_list.append(total_carbon / n_days)
        
        return {
            'poer_gini': {'mean': np.mean(poer_ginis), 'std': np.std(poer_ginis)},
            'fpoe_gini': {'mean': np.mean(fpoe_ginis), 'std': np.std(fpoe_ginis)},
            'poer_carbon': {'mean': np.mean(poer_carbon), 'std': np.std(poer_carbon)},
            'fpoe_carbon': {'mean': np.mean(fpoe_carbon), 'std': np.std(fpoe_carbon)},
        }


def main():
    print("=" * 60)
    print("F-PoER Ablation Study")
    print("=" * 60)
    
    exp = AblationExperiment(seed=42)
    
    print("\n1. Running Ablation Study...")
    ablation_results = exp.run_ablation(n_days=30)
    
    print("\n2. Running Robustness Analysis (100 seeds)...")
    robustness_results = exp.run_robustness(n_seeds=100, n_days=30)
    
    # 保存结果
    output_dir = Path(__file__).parent.parent / 'results'
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / 'ablation_results.json', 'w') as f:
        json.dump(ablation_results, f, indent=2)
    
    with open(output_dir / 'robustness_results.json', 'w') as f:
        json.dump(robustness_results, f, indent=2)
    
    print("\n" + "=" * 60)
    print("Ablation Results (Table 2):")
    print("=" * 60)
    print(f"{'Configuration':<35} {'Gini':<8} {'Top 10%':<10} {'Carbon':<10} {'FS Utility':<12}")
    print("-" * 75)
    for r in ablation_results:
        print(f"{r['name']:<35} {r['gini']:<8.4f} {r['top_10_share']:<10} {r['carbon_kg_day']:<10.1f} {r['fs_utility']:<12.2f}")
    
    print("\n" + "=" * 60)
    print("Robustness Results (Table 3):")
    print("=" * 60)
    print(f"{'Metric':<20} {'PoER':<25} {'F-PoER':<25}")
    print("-" * 70)
    print(f"{'Gini Coefficient':<20} {robustness_results['poer_gini']['mean']:.4f} ± {robustness_results['poer_gini']['std']:.4f}  {robustness_results['fpoe_gini']['mean']:.4f} ± {robustness_results['fpoe_gini']['std']:.4f}")
    print(f"{'Carbon (kg/day)':<20} {robustness_results['poer_carbon']['mean']:.1f} ± {robustness_results['poer_carbon']['std']:.1f}  {robustness_results['fpoe_carbon']['mean']:.1f} ± {robustness_results['fpoe_carbon']['std']:.1f}")
    
    print(f"\n✅ Results saved to {output_dir}")


if __name__ == '__main__':
    main()
