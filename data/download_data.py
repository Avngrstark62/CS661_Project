"""
VentureScope — Dataset Acquisition Script
Downloads the real Crunchbase StartUp Investments dataset from Kaggle.

Source: https://www.kaggle.com/datasets/justinas/startup-investments
Records: 720,020+ across 11 tables
License: CC BY-NC-SA 4.0

Usage:
    python data/download_data.py

Requires: kagglehub (pip install kagglehub)
"""
import os
import sys
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_RAW


def download_dataset():
    """Download the Crunchbase StartUp Investments dataset from Kaggle."""
    print("╔══════════════════════════════════════════════════════╗")
    print("║  VentureScope — Dataset Acquisition                  ║")
    print("║  Source: Kaggle (justinas/startup-investments)        ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    try:
        import kagglehub
    except ImportError:
        print("❌ kagglehub not installed. Install with: pip install kagglehub")
        sys.exit(1)

    print("📥 Downloading from Kaggle...")
    path = kagglehub.dataset_download("justinas/startup-investments")
    print(f"   Downloaded to: {path}\n")

    # Copy to project data/raw directory
    os.makedirs(DATA_RAW, exist_ok=True)
    csv_files = [f for f in os.listdir(path) if f.endswith(".csv")]

    for f in csv_files:
        src = os.path.join(path, f)
        dst = os.path.join(DATA_RAW, f)
        shutil.copy2(src, dst)
        size_mb = os.path.getsize(dst) / (1024 * 1024)
        print(f"   ✓ {f:30s} ({size_mb:.1f} MB)")

    print(f"\n✅ {len(csv_files)} files copied to {DATA_RAW}")
    print("\nNext step: Run preprocessing")
    print("  python preprocessing/clean.py")


if __name__ == "__main__":
    download_dataset()
