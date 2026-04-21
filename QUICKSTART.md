# PoER Fairness Study - 快速入门指南

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
- ✅ 生成对比报告
- ✅ 生成所有图表

### 3. 查看结果

**数据文件:** `data/` 目录
- `results.json` - 原始 PoER 结果
- `results_fpoe.json` - F-PoER 结果

**图表文件:** `paper/figures/` 目录
- `gini_comparison.svg` - 基尼系数对比图
- `gini_time_series.svg` - 时间演化曲线
- `utility_comparison.svg` - 效用箱线图
- `mechanism_diagram.svg` - 机制示意图

---

## 📊 预期结果

运行完成后，你应该看到：

```
原始 PoER:
  基尼系数：~0.85 ❌
  碳减排：~351 kg/day

F-PoER:
  基尼系数：~0.16 ✅
  碳减排：~355 kg/day
  公平性改善：~81%
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

### 生成图表

```bash
cd scripts
python3 generate_all_figures.py
```

---

## 📝 编译论文 PDF

```bash
cd paper
pdflatex paper_main.tex
bibtex paper_main.aux
pdflatex paper_main.tex
pdflatex paper_main.tex
```

输出：`paper_main.pdf`

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

---

## 📞 需要帮助？

- 📖 完整文档：查看 `README.md`
- 🐛 报告问题：https://github.com/openclaw/poer-fairness-study/issues
- 📧 联系作者：corresponding@author.edu

---

**祝实验顺利！** 🎉
