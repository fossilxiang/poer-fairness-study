# Overleaf 编译说明

**项目:** PoER Fairness Study - Revised Paper  
**主文件:** `paper_main_revised.tex`  
**更新日期:** 2026-04-22

---

## 📝 编译步骤

### 1. 上传文件到 Overleaf

1. 访问 https://www.overleaf.com/project
2. 登录或注册 (免费账号即可)
3. 点击 **"New Project"** → **"Upload Project"**
4. 选择本目录下的所有文件:
   - `paper_main_revised.tex` (主文件)
   - `references.bib` (参考文献)
   - `figures/` 目录 (如果有图片)

### 2. 设置主文件

- Overleaf 会自动识别 `.tex` 文件
- 确保 `paper_main_revised.tex` 被设为主文件 (右键 → Set as Main Document)

### 3. 编译

点击 **"Recompile"** 按钮 (绿色圆形图标)

**编译顺序:**
1. PDFLaTeX (第一次)
2. BibTeX
3. PDFLaTeX (第二次)
4. PDFLaTeX (第三次)

Overleaf 会自动处理这些步骤，通常只需点击一次 Recompile。

### 4. 下载 PDF

编译成功后:
1. 点击左上角菜单图标 (≡)
2. 找到 `paper_main_revised.pdf`
3. 点击下载图标

---

## ⚠️ 可能的问题

### 缺少 .sty 文件

如果提示缺少某个 .sty 文件:
- Overleaf 通常会自动安装
- 如果失败，在菜单中勾选 "Use TeX Live 2023" 或更新版本

### 图片缺失

确保 `figures/` 目录已上传，且图片格式为:
- PDF (推荐)
- EPS
- PNG (位图)
- JPG (位图)

### 参考文献不显示

- 确保 `references.bib` 已上传
- 确保 `.tex` 文件中有 `\bibliography{references}`
- 重新编译 (Overleaf 会自动运行 BibTeX)

---

## 📊 预期输出

编译成功后应生成约 **15-20 页** 的 PDF，包含:

- 标题页 (Title, Authors, Abstract)
- Introduction
- Results (含 Table 1-4, Figure 1-4)
- Discussion
- Methods
- Conclusion
- References (约 20 篇)

---

## 🔗 相关链接

- Overleaf 教程：https://www.overleaf.com/learn
- LaTeX 符号表：https://www.overleaf.com/learn/latex/Mathematical_fonts
- BibTeX 格式：https://www.overleaf.com/learn/latex/Bibliography_management_with_bibtex

---

**编译时间:** 约 30-60 秒  
**PDF 大小:** 约 1-2 MB

**祝编译顺利！** 🎉
