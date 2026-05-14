from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SCRIPTS = [
    "download_gdp.py",
    "download_inflation.py",
    "download_inequality.py",
    "download_welfare_distribution.py",
    "download_comparative_growth_inequality.py",
    "download_poverty.py",
    "download_labor.py",
    "download_cost_of_living.py",
]


if __name__ == "__main__":
    scripts_dir = Path(__file__).resolve().parent
    for script in SCRIPTS:
        print(f"Running {script}")
        subprocess.run([sys.executable, str(scripts_dir / script)], check=True)
