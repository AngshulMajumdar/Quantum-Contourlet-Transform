#!/usr/bin/env python3
"""One-command reproduction entry point."""
import subprocess
import sys

commands = [
    [sys.executable, "verify_install.py"],
    [sys.executable, "run_experiments.py", "--shots", "8192", "--seed", "271828", "--output-dir", "results"],
]
for command in commands:
    print("\n$", " ".join(command), flush=True)
    subprocess.run(command, check=True)
print("\nDone. Open results/RESULTS.md for the generated summary.")
