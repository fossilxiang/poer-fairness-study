#!/bin/bash
# PoER Fairness Study - Run All Experiments
# Usage: bash scripts/run_all_experiments.sh

set -e  # Exit on error

echo "============================================================"
echo "PoER Fairness Study - Complete Experiment Suite"
echo "============================================================"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"
EXPERIMENTS_DIR="$PROJECT_ROOT/experiments"
DATA_DIR="$PROJECT_ROOT/data"

# Create data directory if it doesn't exist
mkdir -p "$DATA_DIR"

echo "Project Root: $PROJECT_ROOT"
echo "Experiments: $EXPERIMENTS_DIR"
echo "Data Output: $DATA_DIR"
echo ""

# ============================================================
# Experiment 1: Original PoER
# ============================================================
echo "============================================================"
echo "Experiment 1/2: Original PoER"
echo "============================================================"
cd "$EXPERIMENTS_DIR"
python3 poer_experiment_simple.py

# Copy results to data directory
cp outputs/results.json "$DATA_DIR/"
echo ""
echo "✓ Results saved to: $DATA_DIR/results.json"
echo ""

# ============================================================
# Experiment 2: F-PoER
# ============================================================
echo "============================================================"
echo "Experiment 2/2: F-PoER (Federated PoER)"
echo "============================================================"
python3 poer_fpoe_experiment.py

# Copy results to data directory
cp outputs/results_fpoe.json "$DATA_DIR/"
echo ""
echo "✓ Results saved to: $DATA_DIR/results_fpoe.json"
echo ""

# ============================================================
# Generate Comparison Report
# ============================================================
echo "============================================================"
echo "Generating Comparison Report"
echo "============================================================"
python3 generate_comparison.py
echo ""

# ============================================================
# Generate Figures
# ============================================================
echo "============================================================"
echo "Generating Figures (SVG format)"
echo "============================================================"
cd "$PROJECT_ROOT/scripts"
python3 generate_all_figures.py
echo ""

# ============================================================
# Summary
# ============================================================
echo "============================================================"
echo "All Experiments Complete!"
echo "============================================================"
echo ""
echo "Output Files:"
echo "  Data:"
echo "    - $DATA_DIR/results.json"
echo "    - $DATA_DIR/results_fpoe.json"
echo "    - $DATA_DIR/chart_data.json"
echo "    - $DATA_DIR/sensitivity_data.json"
echo ""
echo "  Figures:"
echo "    - $PROJECT_ROOT/paper/figures/gini_comparison.svg"
echo "    - $PROJECT_ROOT/paper/figures/gini_time_series.svg"
echo "    - $PROJECT_ROOT/paper/figures/utility_comparison.svg"
echo "    - $PROJECT_ROOT/paper/figures/mechanism_diagram.svg"
echo ""
echo "Expected Results:"
echo "  Original PoER Gini: ~0.85"
echo "  F-PoER Gini: ~0.16"
echo "  Fairness Improvement: ~81%"
echo ""
echo "Next Steps:"
echo "  1. Review results in data/ directory"
echo "  2. Check figures in paper/figures/ directory"
echo "  3. Compile paper: cd paper && pdflatex paper_main.tex"
echo ""
echo "============================================================"
