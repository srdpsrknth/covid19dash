#!/usr/bin/env python
# coding: utf-8
"""
RIVM Data Pipeline
Complete pipeline that fetches and processes COVID-19 data from RIVM.
"""

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

def run_script(script_name):
    """Run a Python script and wait for completion"""
    script_path = SCRIPT_DIR / script_name
    print(f"\n{'='*60}")
    print(f"Running {script_name}...")
    print(f"{'='*60}\n")
    
    result = subprocess.run([sys.executable, str(script_path)], cwd=SCRIPT_DIR)
    
    if result.returncode != 0:
        print(f"\n✗ Error running {script_name}")
        sys.exit(1)
    
    return True


if __name__ == "__main__":
    print("Starting RIVM Data Pipeline...")
    
    # Step 1: Fetch raw data
    run_script("rivm_fetch.py")
    
    # Step 2: Process raw data
    run_script("rivm_process.py")
    
    print("\n" + "="*60)
    print("✓ RIVM Data Pipeline Completed Successfully!")
    print("="*60)




