# 🚀 GitHub 推送与 PDF 编译完整指南

**创建时间:** 2026-04-22 07:58 CST  
**状态:** ⚠️ 需要手动操作

---

## 📋 当前状态

### ✅ 已完成
- [x] 所有文件已本地 commit
- [x] README.md 已更新
- [x] 论文已修订 (paper_main_revised.tex)
- [x] 实验数据已生成
- [x] 图表数据已导出

### ⏳ 待完成
- [ ] 推送到 GitHub (需要认证)
- [ ] 编译 PDF (需要 LaTeX)
- [ ] 验证 GitHub 仓库

---

## 1️⃣ 推送到 GitHub (三种方法)

### 方法 A: 使用 Personal Access Token (推荐)

**步骤:**

1. **创建 Token**
   - 访问：https://github.com/settings/tokens
   - 点击 "Generate new token (classic)"
   - 勾选权限：`repo` (Full control of private repositories)
   - 生成后复制 Token (只显示一次！)

2. **使用 Token 推送**
   ```bash
   cd /home/admin/.openclaw/workspace/poer-fairness-study
   
   # 方法 1: 在 URL 中包含 Token
   git push https://YOUR_USERNAME:YOUR_TOKEN@github.com/fossilxiang/poer-fairness-study.git main
   
   # 方法 2: 配置 credential helper
   git config --global credential.helper store
   git push
   # 第一次输入 Token，之后会记住
   ```

**示例:**
```bash
git push https://fossilxiang:ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@github.com/fossilxiang/poer-fairness-study.git main
```

---

### 方法 B: 使用 SSH Key

**步骤:**

1. **生成 SSH Key (如果没有)**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   # 一路回车
   ```

2. **添加 Public Key 到 GitHub**
   - 复制公钥：
     ```bash
     cat ~/.ssh/id_ed25519.pub
     ```
   - 访问：https://github.com/settings/keys
   - 点击 "New SSH key"，粘贴公钥

3. **切换 Remote URL 为 SSH**
   ```bash
   cd /home/admin/.openclaw/workspace/poer-fairness-study
   git remote set-url origin git@github.com:fossilxiang/poer-fairness-study.git
   git push -u origin main
   ```

---

### 方法 C: 使用 GitHub Desktop 或 Sourcetree

**GitHub Desktop:**
1. 下载：https://desktop.github.com
2. 登录 GitHub 账号
3. 添加本地仓库：File → Add Local Repository
4. 选择 `/home/admin/.openclaw/workspace/poer-fairness-study`
5. 点击 Push origin

**Sourcetree:**
1. 下载：https://www.sourcetreeapp.com
2. 添加现有仓库
3. 点击 Push

---

## 2️⃣ 编译 PDF (三种方法)

### 方法 A: Overleaf (最简单，推荐)

**步骤:**

1. **访问 Overleaf**
   - https://www.overleaf.com/project
   - 登录或注册 (免费)

2. **创建新项目**
   - 点击 "New Project" → "Upload Project"
   - 选择 `paper/` 目录下的所有文件
   - 上传

3. **编译**
   - 主文件选择：`paper_main_revised.tex`
   - 点击 "Recompile"
   - 等待编译完成

4. **下载 PDF**
   - 点击菜单图标 (左上角)
   - 下载 `paper_main_revised.pdf`

**注意:**
- 可能需要上传 `figures/` 目录中的图片
- 如果缺少 .sty 文件，Overleaf 会自动安装

---

### 方法 B: 本地安装 LaTeX (适合长期使用)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended texlive-science bibtex makeindex

# 编译
cd /home/admin/.openclaw/workspace/poer-fairness-study/paper
pdflatex -interaction=nonstopmode paper_main_revised.tex
bibtex paper_main_revised.aux
pdflatex paper_main_revised.tex
pdflatex paper_main_revised.tex

# 清理辅助文件
make clean  # 或手动删除 *.aux *.log *.out *.bbl *.blg
```

**macOS:**
```bash
# 使用 Homebrew
brew install --cask mactex

# 或使用 BasicTeX (更小)
brew install --cask basictex

# 编译
cd paper
pdflatex paper_main_revised.tex
bibtex paper_main_revised.aux
pdflatex paper_main_revised.tex
pdflatex paper_main_revised.tex
```

**Windows:**
1. 下载 MiKTeX: https://miktex.org/download
2. 安装时选择 "Install missing packages on-the-fly"
3. 使用 TeXworks 或 TeXstudio 打开 `paper_main_revised.tex`
4. 点击编译

---

### 方法 C: 使用 Docker (无需安装)

**步骤:**

```bash
# 拉取 LaTeX Docker 镜像
docker pull blang/latex

# 编译
docker run --rm -v $(pwd):/data blang/latex:ubuntu pdflatex -interaction=nonstopmode paper_main_revised.tex
docker run --rm -v $(pwd):/data blang/latex:ubuntu bibtex paper_main_revised.aux
docker run --rm -v $(pwd):/data blang/latex:ubuntu pdflatex -interaction=nonstopmode paper_main_revised.tex
docker run --rm -v $(pwd):/data blang/latex:ubuntu pdflatex -interaction=nonstopmode paper_main_revised.tex

# PDF 会生成在当前目录
```

---

## 3️⃣ 验证 GitHub 仓库

### 检查清单

推送成功后，访问：https://github.com/fossilxiang/poer-fairness-study

**验证项目:**

- [ ] README.md 正确显示 (检查格式、表格、徽章)
- [ ] 文件结构完整 (experiments/, paper/, results/, scripts/)
- [ ] 最新 commit 信息正确
- [ ] 所有新增文件存在:
  - [ ] `REVISION_COMPLETE.md`
  - [ ] `experiments/ablation_study.py`
  - [ ] `paper/paper_main_revised.tex`
  - [ ] `paper/revision_notes.md`
  - [ ] `results/ablation_results.json`
  - [ ] `results/robustness_results.json`
  - [ ] `results/figure_data/*.csv`

### 如果发现问题

**文件缺失:**
```bash
cd /home/admin/.openclaw/workspace/poer-fairness-study
git status  # 检查哪些文件没推送
git add <missing_files>
git commit -m "Add missing files"
git push
```

**README 渲染错误:**
- 检查 Markdown 语法
- 确认图片路径正确
- 在本地用 VS Code 预览

---

## 🎯 快速操作脚本

### 一键推送脚本 (使用 Token)

创建 `quick_push.sh`:

```bash
#!/bin/bash
# 快速推送脚本

TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # 替换为你的 Token
REPO="https://${TOKEN}@github.com/fossilxiang/poer-fairness-study.git"

cd /home/admin/.openclaw/workspace/poer-fairness-study

echo "Adding all changes..."
git add -A

echo "Committing..."
git commit -m "Update: Revised paper with ablation study (2026-04-22)"

echo "Pushing to GitHub..."
git push $REPO main

echo "Done!"
```

使用:
```bash
chmod +x quick_push.sh
./quick_push.sh
```

---

## 📞 遇到问题？

### 常见错误及解决方案

**错误:** `fatal: could not read Username`
- **解决:** 使用 Token 或配置 SSH

**错误:** `Permission denied (publickey)`
- **解决:** 检查 SSH key 是否正确添加到 GitHub

**错误:** `LaTeX Error: File xxx.sty not found`
- **解决:** 安装缺失的 package 或使用 Overleaf

**错误:** `bibtex: command not found`
- **解决:** 安装 bibtex: `sudo apt-get install bibtex`

---

## 📧 需要帮助？

- 📖 Overleaf 教程：https://www.overleaf.com/learn
- 🔑 GitHub Token 指南：https://docs.github.com/en/authentication
- 🐛 报告问题：https://github.com/fossilxiang/poer-fairness-study/issues

---

**祝顺利！** 🎉

**最后更新:** 2026-04-22 07:58 CST
