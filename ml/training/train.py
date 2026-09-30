#!/usr/bin/env python3
"""
ChurnSense AI — Standalone Model Training & Benchmarking Pipeline

Trains, evaluates, and optionally serializes churn prediction models
from the command line without requiring a running database server.

Usage:
    python ml/training/train.py --data ml/data/synthetic/demo.csv --algorithm random_forest
    python ml/training/train.py --data ml/data/synthetic/demo.csv --benchmark-all
"""

import argparse
import os
import sys
from pathlib import Path

# Add backend directory to Python path for access to app.ml components
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.ml.training.trainer import ModelTrainer


def train_single_model(csv_path: str, algorithm: str, output_dir: str = None):
    print(f"\n==========================================")
    print(f" Training: {algorithm.upper()}")
    print(f"==========================================")

    trainer = ModelTrainer()
    results = trainer.train(
        csv_path=csv_path,
        target_col="Churn",
        algorithm=algorithm,
        output_dir=output_dir or "./ml/models",
    )

    test_metrics = next(m for m in results["metrics"] if m.get("split") == "test")
    print("\n--- Test Split Evaluation Metrics ---")
    print(f"  Accuracy:  {test_metrics['accuracy']:.4f}")
    print(f"  Precision: {test_metrics['precision']:.4f}")
    print(f"  Recall:    {test_metrics['recall']:.4f}")
    print(f"  F1 Score:  {test_metrics['f1_score']:.4f}")
    print(f"  ROC-AUC:   {test_metrics['roc_auc']:.4f}")
    print(f"  Training Time: {results['training_time_seconds']:.2f}s")
    print("---------------------------------------")

    return test_metrics


def main():
    parser = argparse.ArgumentParser(description="ChurnSense AI Model Training Pipeline")
    parser.add_argument(
        "--data",
        type=str,
        default=str(REPO_ROOT / "ml" / "data" / "synthetic" / "demo.csv"),
        help="Path to training CSV dataset",
    )
    parser.add_argument(
        "--algorithm",
        type=str,
        default="random_forest",
        choices=["logistic_regression", "decision_tree", "random_forest", "gradient_boosting", "xgboost"],
        help="Classification algorithm",
    )
    parser.add_argument(
        "--benchmark-all",
        action="store_true",
        help="Train and compare all 5 algorithms",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./ml/models",
        help="Directory to save trained model artifacts (optional)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"Error: Dataset not found at '{args.data}'.")
        print("Run 'python scripts/generate_demo_data.py' to generate synthetic data.")
        sys.exit(1)

    print(f"Loading dataset: {args.data}")

    if args.benchmark_all:
        algorithms = [
            "logistic_regression",
            "decision_tree",
            "random_forest",
            "gradient_boosting",
            "xgboost",
        ]
        comparison = {}
        for algo in algorithms:
            try:
                comparison[algo] = train_single_model(args.data, algo, args.output_dir)
            except Exception as e:
                print(f"Algorithm {algo} failed: {e}")

        print("\n" + "=" * 55)
        print(" MODEL BENCHMARK COMPARISON TABLE")
        print("=" * 55)
        print(f"{'Algorithm':<22} {'Accuracy':<10} {'F1':<8} {'ROC-AUC':<8}")
        print("-" * 55)
        for algo, m in comparison.items():
            print(f"{algo:<22} {m['accuracy']:<10.4f} {m['f1_score']:<8.4f} {m['roc_auc']:<8.4f}")
        print("=" * 55)
    else:
        train_single_model(args.data, args.algorithm, args.output_dir)


if __name__ == "__main__":
    main()
