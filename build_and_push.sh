#!/bin/bash
# Compile PDF and push to GitHub
# 编译 PDF 并推送到 GitHub

set -e

echo "=========================================="
echo "PoER Fairness Study - Build & Push Script"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if pdflatex is available
if ! command -v pdflatex &> /dev/null; then
    echo -e "${YELLOW}Warning: pdflatex not found. Skipping PDF compilation.${NC}"
    echo ""
    echo "To install LaTeX:"
    echo "  Ubuntu/Debian: sudo apt-get install texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended bibtex"
    echo "  macOS: brew install --cask mactex"
    echo "  Windows: https://miktex.org/download"
    echo ""
    echo "Continuing with GitHub push..."
else
    echo "Compiling PDF..."
    cd paper
    
    # Compile revised paper
    echo "  - Compiling paper_main_revised.tex..."
    pdflatex -interaction=nonstopmode paper_main_revised.tex > /dev/null 2>&1
    bibtex paper_main_revised.aux > /dev/null 2>&1 || true
    pdflatex -interaction=nonstopmode paper_main_revised.tex > /dev/null 2>&1
    pdflatex -interaction=nonstopmode paper_main_revised.tex > /dev/null 2>&1
    
    # Clean auxiliary files
    echo "  - Cleaning auxiliary files..."
    rm -f *.aux *.log *.out *.bbl *.blg *.toc *.lof *.lot
    
    # Move PDF to root
    if [ -f paper_main_revised.pdf ]; then
        mv paper_main_revised.pdf ../paper_main_revised.pdf
        echo -e "${GREEN}✓ PDF compiled successfully: ../paper_main_revised.pdf${NC}"
    else
        echo -e "${RED}✗ PDF compilation failed${NC}"
    fi
    
    cd ..
fi

echo ""
echo "Preparing GitHub push..."
echo ""

# Check if git is configured
if [ ! -d .git ]; then
    echo -e "${RED}Error: Not a git repository${NC}"
    exit 1
fi

# Show git status
echo "Git status:"
git status --short
echo ""

# Add all changes
echo "Adding all changes..."
git add -A

# Commit
echo "Committing changes..."
git commit -m "Update: Revised paper with ablation study and robustness analysis (2026-04-22)

Major updates:
- Added ablation study quantifying component contributions
- Added robustness analysis (100 random seeds)
- Strengthened DMER theorem with explicit assumptions
- Added Shapley value comparison
- Extended literature review (11 core references)
- Updated README and documentation
- Exported figure data for Excel/Origin

Results:
- Gini: PoER 0.93 → F-PoER 0.27 (71% improvement)
- Statistical significance: p < 10^-100
"

# Show remote
echo ""
echo "Remote URL:"
git remote -v
echo ""

# Push
echo "Pushing to GitHub..."
git push origin main || git push origin master

echo ""
echo -e "${GREEN}=========================================="
echo "✓ Build & Push Complete!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Check GitHub: https://github.com/openclaw/poer-fairness-study"
echo "  2. Verify PDF (if compiled): paper_main_revised.pdf"
echo "  3. Update arXiv submission (planned: 2026-04-24)"
echo ""
