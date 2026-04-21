#!/usr/bin/env python3
"""
Generate All Figures for PoER Fairness Study Paper
Usage: python3 scripts/generate_all_figures.py
"""

import sys
import os
from pathlib import Path

# Add experiments directory to path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root / 'experiments'))

# Import the figure generation script
generate_script = project_root / 'paper' / 'generate_figures_svg.py'

if generate_script.exists():
    print(f"Running: {generate_script}")
    exec(compile(generate_script.read_text(), str(generate_script), 'exec'))
else:
    print(f"Error: Figure generation script not found at {generate_script}")
    sys.exit(1)

print("\n✓ All figures generated successfully!")
print(f"Output directory: {project_root}/paper/figures/")
