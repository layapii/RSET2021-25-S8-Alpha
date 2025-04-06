import subprocess
import sys

PYTHON_PATH = sys.executable  # Uses the same Python as your terminal
PROTEINMPNN_PATH = "ProteinMPNN/protein_mpnn_run.py"

subprocess.run([PYTHON_PATH, PROTEINMPNN_PATH], check=True)
