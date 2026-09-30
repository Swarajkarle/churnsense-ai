# ChurnSense AI — Model Artifacts Store

This directory is designated for local serialization and loading of trained machine learning model weights, preprocessor state objects, and explainability artifacts (`.joblib`, `.pkl`).

---

## Artifact Policy & Git Exclusion

In accordance with machine learning engineering best practices:
- **Binary model files are excluded from Git version control** (configured in `.gitignore`).
- Committing large opaque binary artifacts inflates repository size and degrades reproducibility.
- Models should be trained and validated locally using code definitions and tracked dataset versions.

---

## Reproducible Model Training

To train the complete set of predictive models from scratch on the synthetic demo dataset or a custom dataset, execute:

```bash
# Using the backend training pipeline
cd backend
python -m app.ml.training.trainer --data ../ml/data/synthetic/demo.csv

# Or via the standalone training script
python ml/training/train.py --data ml/data/synthetic/demo.csv --algorithm random_forest
```

### Supported Algorithms
1. `logistic_regression`: L2-regularized linear baseline
2. `decision_tree`: Rule-partitioning tree
3. `random_forest`: 100-estimator ensemble bagging classifier
4. `gradient_boosting`: Sequential gradient boosting
5. `xgboost`: Regularized extreme gradient boosting

Trained artifacts will be saved with their respective preprocessor states to allow seamless inference and SHAP explainability.
