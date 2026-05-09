import subprocess
import os
import sys
from pathlib import Path

def run_step(name, script_path):
    print(f"\n{'='*50}")
    print(f"RUNNING STEP: {name}")
    print(f"{'='*50}")
    
    # Use the current python executable from the venv
    python_exe = sys.executable
    
    # Set PYTHONPATH to root
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd())
    
    result = subprocess.run([python_exe, script_path], env=env)
    
    if result.returncode != 0:
        print(f"\nERROR: Step '{name}' failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    else:
        print(f"\nSUCCESS: Step '{name}' completed.")

def main():
    steps = [
        ("Extraction", "src/phase1_ingestion/subphase1_1_extraction/main.py"),
        ("Cleaning", "src/phase1_ingestion/subphase1_2_cleaning/cleaner.py"),
        ("Chunking", "src/phase1_ingestion/subphase1_3_chunking/chunker.py"),
        ("Embedding", "src/phase1_ingestion/subphase1_4_embedding/embedder.py"),
    ]
    
    for name, path in steps:
        run_step(name, path)
    
    print("\n" + "="*50)
    print("SCHEDULER TEST COMPLETE: All steps succeeded!")
    print("="*50)

if __name__ == "__main__":
    main()
