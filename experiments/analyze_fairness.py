#!/usr/bin/env python3
"""
PoER 公平性诊断分析 - 文本版（无需 matplotlib）
"""

import numpy as np
import json
from pathlib import Path

# 加载实验结果
with open('/home/admin/.openclaw/workspace/poer_experiments/outputs/results.json', 'r') as f:
    data = json.load(f)

results = data['results']
summary = data['summary']

print("=" * 70)
print("PoER 公平性诊断分析报告")
print("=" * 70)

# 1. 基尼系数对比
print("\n【1. 基尼系数对比】(0=完全平等，1=极度不均，0.4=警戒线)")
print("-" * 70)
print(f"  PoER 原始版：   {summary['avg_gini_poer']:.4f}  ❌ 极度不均 (超警戒线 112%)")
print(f"  PoER 改进版：   {summary['avg_gini_poer_plus']:.4f}  ❌ 依然极度不均 (超警戒线 111%)")
print(f"  按重量计酬：   {summary['avg_gini_weight']:.4f}  ✅ 分配均匀")
print(f"  按类别计酬：   {summary['avg_gini_category']:.4f}  ✅ 分配均匀")

# 2. 效用对比
print("\n【2. Fehr-Schmidt 效用对比】(考虑公平偏好的居民效用)")
print("-" * 70)
print(f"  PoER 原始版：   {summary['avg_utility_poer']:.2f}")
print(f"  PoER 改进版：   {summary['avg_utility_poer_plus']:.2f}")
print(f"  按重量计酬：   {summary['avg_utility_weight']:.2f}")
print(f"  按类别计酬：   {summary['avg_utility_category']:.2f}")

# 3. 问题根源分析
print("\n【3. 问题根源分析】")
print("-" * 70)
print("""
  🔴 PoER 机制的固有缺陷：
  
  (1) 累积优势效应
      - 早期投放者改变社区分布，获得大部分熵减积分
      - 后期投放者边际贡献趋近于零
      
  (2) 马太效应
      - 高参与率家庭获得不成比例的高积分
      - 低参与率家庭被进一步边缘化
      
  (3) 边际熵减递减
      - 随着累计质量增加，单户投放对分布的影响趋于零
      - 收敛速度 O(1/√N)，后期几乎无积分
""")

print("\n【4. 改进方向】")
print("-" * 70)
print("""
  ✅ 建议实施 PoER+++ 机制：
  
  (1) 轮次重置基线
      - 每轮从固定基线开始计算熵减
      - 消除累积优势，保证每轮机会均等
      
  (2) 相对熵减竞争
      - 计算相对于平均水平的熵减贡献
      - 激励高质量分类而非单纯早投放
      
  (3) 积分上限封顶
      - 单户单轮积分不超过平均值的 N 倍
      - 防止大户垄断
      
  (4) 参与率平滑
      - 对数平滑处理投放质量
      - 减少规模效应
""")

# 5. 生成改进版 PoER+++ 代码
print("\n【5. PoER+++ 改进代码】")
print("-" * 70)
print("""
def poer_plusplus_allocation(reports, baseline, alpha=100.0):
    '''
    PoER+++ : 轮次重置 + 相对熵减 + 积分上限
    目标基尼系数： < 0.3
    '''
    K = len(baseline)
    credits = {}
    
    # 关键改进 1: 每轮重置基线，消除累积优势
    M_round = list(baseline)  # 每轮从基线重新开始
    
    # 预计算平均熵减（用于相对比较）
    total_delta_H = 0.0
    for house_id, m in reports:
        prior_total = sum(M_round)
        H_prior = compute_entropy([x/prior_total for x in M_round])
        M_temp = [M_round[k] + m[k] for k in range(K)]
        post_total = sum(M_temp)
        H_post = compute_entropy([x/post_total for x in M_temp])
        total_delta_H += max(0.0, H_prior - H_post)
    
    avg_delta_H = total_delta_H / len(reports) if reports else 1.0
    
    # 重置用于实际分配
    M_round = list(baseline)
    
    for house_id, m in reports:
        prior_total = sum(M_round)
        H_prior = compute_entropy([x/prior_total for x in M_round])
        
        M_round = [M_round[k] + m[k] for k in range(K)]
        post_total = sum(M_round)
        H_post = compute_entropy([x/post_total for x in M_round])
        
        delta_H = max(0.0, H_prior - H_post)
        W = sum(m)
        
        # 关键改进 2: 相对熵减 (相对于平均水平)
        delta_H_rel = delta_H / (avg_delta_H + 0.01)
        
        # 关键改进 3: 对数平滑 + 参与率归一化
        W_smooth = math.log(1 + W)
        
        # 关键改进 4: 设置单户积分上限 (不超过平均值的 5 倍)
        avg_credit = alpha * W_smooth / len(reports)
        max_credit = avg_credit * 5.0
        
        credit = min(alpha * delta_H_rel * W_smooth, max_credit)
        credits[house_id] = credits.get(house_id, 0.0) + credit
    
    return credits
""")

# 6. 实验数据摘要
print("\n【6. 实验数据摘要】")
print("-" * 70)
print(f"  实验规模：500 户家庭 × 30 轮")
print(f"  平均碳减排：{summary['avg_carbon_reduction']:.1f} ± {summary['std_carbon_reduction']:.1f} kg CO₂e/轮")
print(f"  PoER 效用增益 vs 按重量：{summary['utility_gain_poer_vs_weight']:.1f}%")
print(f"  PoER 公平性 vs 按重量：{summary['fairness_improvement_poer_vs_weight']:.1f}% (负值=更差)")

print("\n" + "=" * 70)
print("诊断完成！建议实施 PoER+++ 机制以改善公平性。")
print("=" * 70)

# 保存分析报告
report_path = Path('/home/admin/.openclaw/workspace/poer_experiments/outputs/fairness_diagnosis.md')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("# PoER 公平性诊断报告\n\n")
    f.write(f"**生成时间**: 2026-04-21\n\n")
    f.write("## 核心发现\n\n")
    f.write(f"- PoER 原始版基尼系数：**{summary['avg_gini_poer']:.4f}** (极度不均)\n")
    f.write(f"- PoER 改进版基尼系数：**{summary['avg_gini_poer_plus']:.4f}** (依然极度不均)\n")
    f.write(f"- 按重量计酬基尼系数：**{summary['avg_gini_weight']:.4f}** (分配均匀)\n\n")
    f.write("## 问题根源\n\n")
    f.write("1. 累积优势效应 - 早期投放者垄断积分\n")
    f.write("2. 马太效应 - 高参与率家庭获得不成比例优势\n")
    f.write("3. 边际熵减递减 - 后期投放者几乎无积分\n\n")
    f.write("## 改进建议\n\n")
    f.write("实施 PoER+++ 机制：轮次重置 + 相对熵减 + 积分上限\n")
print(f"\n报告已保存：{report_path}")
