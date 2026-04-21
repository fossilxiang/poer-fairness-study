# PoER Fairness Study - 快速入门指南

**版本:** 1.1.0 (Revised)  
**更新日期:** 2026-04-22

---

## 🚀 5 分钟快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/openclaw/poer-fairness-study.git
cd poer-fairness-study
```

### 2. 运行所有实验（一键完成）

```bash
bash scripts/run_all_experiments.sh
```

这将自动执行：
- ✅ 原始 PoER 实验
- ✅ F-PoER 实验
- ✅ 消融实验 (Ablation Study) ⭐ 新增
- ✅ 鲁棒性分析 (100 种子) ⭐ 新增
- ✅ 生成对比报告
- ✅ 生成所有图表

### 3. 查看结果

**数据文件:** `results/` 目录 (Updated ⭐)
- `ablation_results.json` - 消融实验结果 ⭐ 新增
- `robustness_results.json` - 鲁棒性分析 ⭐ 新增
- `figure_data/` - 图表数据 (CSV/JSON) ⭐ 新增

**图表文件:** `paper/figures/` 目录
- `gini_comparison.svg` - 基尼系数对比图
- `gini_time_series.svg` - 时间演化曲线
- `lorenz_curves.svg` - 洛伦兹曲线 ⭐ 新增
- `mechanism_diagram.svg` - 机制示意图

---

## 📊 预期结果 (Updated ⭐)

运行完成后，你应该看到：

```
原始 PoER:
  基尼系数：~0.93 ❌
  Top 10% 份额：~97%
  碳减排：~1000 kg/day

F-PoER:
  基尼系数：~0.27 ✅
  Top 10% 份额：~17%
  碳减排：~1000 kg/day
  公平性改善：~71%

消融实验:
  + 时间窗口 (W=6):    Gini ~0.52 (44% 改善)
  + 相对熵减：Gini ~0.34 (35% 改善)
  + 混合分配 (50:50):  Gini ~0.27 (71% 总改善)

鲁棒性分析 (100 种子):
  PoER Gini:  0.9250 ± 0.0071
  F-PoER Gini: 0.2715 ± 0.0101
  p-value: < 10^-100
```

---

## 🔧 单独运行实验

### 只运行原始 PoER

```bash
cd experiments
python3 poer_experiment_simple.py
```

### 只运行 F-PoER

```bash
cd experiments
python3 poer_fpoe_experiment.py
```

### 运行消融实验 ⭐ 新增

```bash
cd experiments
python3 ablation_study.py
```

### 运行鲁棒性分析 ⭐ 新增

```bash
# 在 Python 中调用
cd experiments
python3 -c "from ablation_study import AblationExperiment; \
  exp = AblationExperiment(); \
  results = exp.run_robustness(n_seeds=100)"
```

### 生成图表

```bash
cd scripts
python3 generate_all_figures.py
```

### 导出图表数据 (用于 Excel/Origin) ⭐ 新增

```bash
cd scripts
python3 export_figure_data.py
```

---

## 📝 编译论文 PDF (Updated ⭐)

### 编译修订版论文

```bash
cd paper
pdflatex paper_main_revised.tex
bibtex paper_main_revised.aux
pdflatex paper_main_revised.tex
pdflatex paper_main_revised.tex
```

输出：`paper_main_revised.pdf`

### 清理辅助文件

```bash
# 删除编译生成的临时文件
rm -f *.aux *.log *.out *.bbl *.blg
```

### ⚠️ 注意事项

1. **页眉页脚:** 编译时删除包含 `file://` 的本地路径链接
2. **字体嵌入:** 确保所有字体已嵌入（投稿要求）
3. **图片格式:** 使用 PDF 或 EPS 格式的矢量图

---

## 📦 文件结构概览

```
poer-fairness-study/
├── README.md                    # 完整文档
├── QUICKSTART.md                # 本文件
├── REVISION_COMPLETE.md         # 修订说明 ⭐ 新增
│
├── experiments/
│   ├── poer_experiment_simple.py
│   ├── poer_fpoe_experiment.py
│   ├── ablation_study.py        # 消融实验 ⭐ 新增
│   └── ...
│
├── paper/
│   ├── paper_main.tex
│   ├── paper_main_revised.tex   # 修订版 ⭐ 新增
│   ├── revision_notes.md        # 修改说明 ⭐ 新增
│   └── figures/
│
├── results/                     # 结果目录 ⭐ 更新
│   ├── ablation_results.json
│   ├── robustness_results.json
│   └── figure_data/
│
└── scripts/
    ├── export_figure_data.py    # 数据导出 ⭐ 新增
    └── ...
```

---

## ❓ 常见问题

### Q: 安装依赖报错？
A: 只需要 Python 3.6+ 和 NumPy（可选）。大部分实验只用标准库。

```bash
pip install numpy  # 可选，加速计算
```

### Q: 结果与预期不符？
A: 允许 ±2% 的随机波动。如需完全一致，确保随机种子为 42。

### Q: 图表无法显示？
A: SVG 文件可用浏览器打开，或用 Inkscape/AI 编辑。

```bash
# 在浏览器中打开
firefox paper/figures/gini_comparison.svg
```

### Q: 如何引用修订版？⭐ 新增
A: 使用以下 BibTeX：

```bibtex
@article{fossil2026collapse,
  title={The Collapse of Incentives: Fairness-Efficiency Trade-off in Entropy-Driven Carbon Credit Allocation},
  author={Fossil and Friday AI},
  journal={arXiv preprint arXiv:2604.xxxxx},
  year={2026},
  note={Revised: 2026-04-22. Ablation study and robustness analysis added}
}
```

### Q: 消融实验运行时间太长？
A: 完整消融实验约需 30 分钟。可以：
- 减少模拟天数（修改 `n_days` 参数）
- 减少随机种子数量（修改 `n_seeds` 参数）
- 使用已有结果：`results/ablation_results.json`

---

## 📞 需要帮助？

- 📖 完整文档：查看 `README.md`
- 🐛 报告问题：https://github.com/openclaw/poer-fairness-study/issues
- 📧 联系作者：corresponding@author.edu
- 📝 修订说明：查看 `REVISION_COMPLETE.md` ⭐ 新增

---

## 🔗 快速链接

- [完整 README](README.md)
- [修订说明](REVISION_COMPLETE.md)
- [文献综述](paper/literature_review.md)
- [修改笔记](paper/revision_notes.md)
- [GitHub Issues](https://github.com/openclaw/poer-fairness-study/issues)

---

**祝实验顺利！** 🎉

**最后更新:** 2026-04-22  
**版本:** 1.1.0 (Revised)
