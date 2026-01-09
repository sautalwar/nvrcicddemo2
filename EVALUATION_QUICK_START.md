# Evaluation Framework - Quick Reference

## 🎯 Overview

The evaluation framework provides automated quality assurance for ML models and data pipelines with:
- **Model Performance Evaluation** - Classification metrics, cross-validation, threshold checks
- **Data Quality Assessment** - 6-dimensional quality validation
- **Automated Reporting** - JSON reports with detailed metrics

## 🚀 Quick Start

### Run Complete Evaluation
```bash
python scripts/run_evaluation.py
```

### Run Data Quality Only
```python
from scripts.evaluate_data_quality import DataQualityEvaluator
import pandas as pd

df = pd.read_csv('sample_customer_data.csv')
evaluator = DataQualityEvaluator(df, 'Customer Data')
evaluator.check_completeness()
evaluator.check_uniqueness(['customer_id'])
evaluator.print_report()
```

### Run Model Evaluation Only
```python
from scripts.evaluate_model import ModelEvaluator

evaluator = ModelEvaluator(model, X_test, y_test)
evaluator.predict()
evaluator.calculate_classification_metrics()
evaluator.check_performance_thresholds()
evaluator.print_report()
```

## 📊 What Gets Evaluated

### Model Metrics
- ✅ Accuracy
- ✅ Precision
- ✅ Recall
- ✅ F1-Score
- ✅ ROC-AUC
- ✅ Confusion Matrix
- ✅ Cross-Validation Scores

### Data Quality Dimensions
1. **Completeness** - Missing values
2. **Uniqueness** - Duplicate records
3. **Consistency** - Business rule violations
4. **Accuracy** - Values within expected ranges
5. **Timeliness** - Data freshness
6. **Validity** - Format and type validation

## 🎚️ Default Thresholds

### Model Performance
| Metric | Minimum |
|--------|---------|
| Accuracy | 70% |
| Precision | 65% |
| Recall | 60% |
| F1-Score | 65% |

### Data Quality
| Check | Threshold |
|-------|-----------|
| Null Values | < 5% per column |
| Duplicates | 0 for key columns |
| Business Rules | 100% compliance |
| Value Ranges | 100% within bounds |

## 📁 Output Files

All reports are saved to `reports/` directory:
- `data_quality_report.json` - Data quality assessment
- `model_evaluation.json` - Model performance metrics

## 🔄 CI/CD Integration

Evaluation runs automatically on:
- Pull requests (data quality checks)
- Model training completion (performance validation)
- Manual workflow dispatch

GitHub Actions workflow: `.github/workflows/model-evaluation.yml`

## 💡 Common Use Cases

### Before Model Training
```python
# Validate training data quality
evaluator = DataQualityEvaluator(train_df, 'Training Data')
evaluator.check_completeness()
evaluator.check_consistency(business_rules)
if len(evaluator.failed) > 0:
    raise Exception("Data quality issues found")
```

### After Model Training
```python
# Validate model meets requirements
evaluator = ModelEvaluator(model, X_test, y_test, X_train, y_train)
evaluator.predict()
evaluator.calculate_classification_metrics()
evaluator.check_performance_thresholds()

if not evaluator.metrics['threshold_checks']['all_passed']:
    print("Model does not meet performance thresholds")
```

### Custom Thresholds
```python
# Set stricter requirements for production
prod_thresholds = {
    'accuracy': 0.85,
    'precision': 0.80,
    'recall': 0.75,
    'f1_score': 0.80
}
evaluator.check_performance_thresholds(prod_thresholds)
```

## 🛠️ Customization

### Add Custom Data Quality Rules
```python
# Define business-specific rules
consistency_rules = {
    'sales_positive': lambda row: row['sales'] >= 0,
    'email_format': lambda row: '@' in str(row['email']),
    'age_reasonable': lambda row: 0 <= row['age'] <= 120
}

evaluator.check_consistency(consistency_rules)
```

### Add Custom Validation
```python
# Custom field validators
validation_rules = {
    'email': lambda x: isinstance(x, str) and '@' in x and '.' in x,
    'phone': lambda x: len(str(x)) >= 10,
    'zip_code': lambda x: len(str(x)) == 5
}

evaluator.check_validity(validation_rules)
```

## 📈 Sample Output

```
======================================================================
DATA QUALITY EVALUATION REPORT
Generated: 2026-01-08 18:10:28
======================================================================

Dataset: Customer Churn Dataset
Shape: 100 rows × 7 columns

COMPLETENESS CHECKS
----------------------------------------------------------------------
  ✅ customer_id                   : 0.00% nulls (threshold: 5.00%)
  ✅ total_purchases               : 0.00% nulls (threshold: 5.00%)

SUMMARY
----------------------------------------------------------------------
  Total Checks: 19
  Passed: 19
  Failed: 0
  Success Rate: 100.0%

  ✅ All data quality checks passed!
======================================================================
```

## 🔗 Related Documentation

- [Full Documentation](EVALUATION_FRAMEWORK.md)
- [Model Training Pipeline](MODEL_TRAINING_PIPELINE_EXPLAINED.md)
- [Setup Guide](SETUP.md)

## 📞 Support

For issues or questions:
1. Check the full documentation in `EVALUATION_FRAMEWORK.md`
2. Review workflow logs in GitHub Actions
3. Contact the DevOps team
