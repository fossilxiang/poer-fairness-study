#!/bin/bash
# Push to GitHub - PoER Fairness Study
# Usage: bash push_to_github.sh

set -e

GITHUB_USERNAME="fossilxiang"
REPO_NAME="poer-fairness-study"
REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo "============================================================"
echo "Push PoER Fairness Study to GitHub"
echo "============================================================"
echo ""
echo "Repository: ${GITHUB_USERNAME}/${REPO_NAME}"
echo "Remote URL: ${REPO_URL}"
echo ""

# Check if remote exists
if git remote | grep -q "^origin$"; then
    echo "✓ Remote 'origin' already configured"
    git remote -v
else
    echo "Adding remote repository..."
    git remote add origin ${REPO_URL}
fi

echo ""
echo "============================================================"
echo "Pushing to GitHub..."
echo "============================================================"
echo ""

# Try to push
if git push -u origin main; then
    echo ""
    echo "============================================================"
    echo "✅ Success! Repository pushed to GitHub"
    echo "============================================================"
    echo ""
    echo "📦 View your repository at:"
    echo "   https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Add repository topics (carbon-credit, waste-sorting, etc.)"
    echo "   2. Check GitHub Actions tab for CI/CD status"
    echo "   3. Share the repository link!"
    echo ""
else
    echo ""
    echo "============================================================"
    echo "❌ Push failed. Possible solutions:"
    echo "============================================================"
    echo ""
    echo "Option 1: Use GitHub Personal Access Token"
    echo "   1. Visit: https://github.com/settings/tokens"
    echo "   2. Create a new token with 'repo' scope"
    echo "   3. Run:"
    echo "      git remote set-url origin https://<TOKEN>@github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
    echo "      git push -u origin main"
    echo ""
    echo "Option 2: Use SSH (if you have SSH keys configured)"
    echo "   git remote set-url origin git@github.com:${GITHUB_USERNAME}/${REPO_NAME}.git"
    echo "   git push -u origin main"
    echo ""
    echo "Option 3: Manual push"
    echo "   1. Create repository at: https://github.com/new"
    echo "   2. Repository name: ${REPO_NAME}"
    echo "   3. DO NOT initialize with README"
    echo "   4. Then run:"
    echo "      git remote add origin https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
    echo "      git branch -M main"
    echo "      git push -u origin main"
    echo ""
fi

echo "============================================================"
