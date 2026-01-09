# Evaluation Framework

This workspace includes a comprehensive evaluation framework for assessing data quality and model performance.

## Components

### 1. Model Evaluation (`scripts/evaluate_model.py`)

Evaluates trained ML models with comprehensive metrics:

- **Classification Metrics**: Accuracy, Precision, Recall, F1-Score, ROC-AUC
- **Confusion Matrix**: True/False Positives and Negatives
- **Cross-Validation**: Model robustness assessment
- **Performance Thresholds**: Automated quality gates

**Usage:**
```python
from scripts.evaluate_model import ModelEvaluator

evaluator = ModelEvaluator(model, X_test, y_test, X_train, y_train)
evaluator.predict()
evaluator.calculate_classification_metrics()
evaluator.evaluate_model_robustness()
evaluator.check_performance_thresholds()
evaluator.print_report()
evaluator.save_report('reports/model_evaluation.json')
```

### 2. Data Quality Evaluation (`scripts/evaluate_data_quality.py`)

Validates data quality across six dimensions:

- **Completeness**: Missing value analysis
- **Uniqueness**: Duplicate detection
- **Consistency**: Business rule validation
- **Accuracy**: Value range verification
- **Timeliness**: Data freshness checks
- **Validity**: Custom validation rules

**Usage:**
```python
from scripts.evaluate_data_quality import DataQualityEvaluator

evaluator = DataQualityEvaluator(df, 'Customer Data')
evaluator.check_completeness(null_threshold=0.05)
evaluator.check_uniqueness(['customer_id'])
evaluator.check_accuracy(value_ranges)
evaluator.print_report()
evaluator.save_report('reports/data_quality_report.json')
```

### 3. Complete Evaluation Suite (`scripts/run_evaluation.py`)

Runs all evaluation checks:

```bash
python scripts/run_evaluation.py
```

This will:
1. Evaluate sample customer data quality
2. Run model performance benchmarks
3. Validate pipeline outputs
4. Generate comprehensive evaluation summary

## Performance Thresholds

Default minimum thresholds for model acceptance:

| Metric    | Minimum Threshold |
|-----------|-------------------|
| Accuracy  | 70%               |
| Precision | 65%               |
| Recall    | 60%               |
| F1-Score  | 65%               |

## Data Quality Standards

Default quality thresholds:

- **Completeness**: < 5% missing values per column
- **Uniqueness**: 0 duplicates for key columns
- **Consistency**: 100% compliance with business rules
- **Accuracy**: 100% values within expected ranges
- **Timeliness**: Data < 30 days old

## Integration with CI/CD

The evaluation framework is integrated into GitHub Actions workflows:

```yaml
- name: Run Evaluation Framework
  run: python scripts/run_evaluation.py
  
- name: Check Model Performance
  run: |
    python -c "
    from scripts.evaluate_model import ModelEvaluator
    # Add model evaluation logic
    "
```

## Reports

Evaluation reports are saved to the `reports/` directory:

- `reports/model_evaluation.json` - Model performance metrics
- `reports/data_quality_report.json` - Data quality assessment
- `reports/evaluation_summary.json` - Overall evaluation summary

## Customization

### Custom Performance Thresholds

```python
custom_thresholds = {
    'accuracy': 0.80,
    'precision': 0.75,
    'recall': 0.70,
    'f1_score': 0.75
}
evaluator.check_performance_thresholds(custom_thresholds)
```

### Custom Data Quality Rules

```python
consistency_rules = {
    'rule_name': lambda row: row['field1'] > row['field2'],
    'email_format': lambda row: '@' in str(row['email'])
}
evaluator.check_consistency(consistency_rules)
```

### Custom Validation Functions

```python
validation_rules = {
    'email': lambda x: isinstance(x, str) and '@' in x,
    'age': lambda x: 0 <= x <= 120
}
evaluator.check_validity(validation_rules)
```

## Best Practices

1. **Run evaluations before deployment** - Ensure quality gates are met
2. **Track metrics over time** - Monitor model drift and data quality trends
3. **Set appropriate thresholds** - Align with business requirements
4. **Document failures** - Investigate and address evaluation failures
5. **Automate in CI/CD** - Make evaluation part of your pipeline

## Troubleshooting

### Evaluation Fails to Run

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify data files exist in expected locations
- Check that the `reports/` directory has write permissions

### Threshold Checks Fail

- Review actual vs. expected metrics in the report
- Adjust thresholds if they're too strict for your use case
- Investigate root causes of poor performance

### Data Quality Issues

- Review failed checks in the detailed report
- Fix data quality issues at the source
- Update validation rules if they're incorrect

## Examples

### Example 1: Evaluate Model Training Results

```python
from scripts.evaluate_model import ModelEvaluator
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Load test data
test_data = pd.read_csv('test_data.csv')
X_test = test_data.drop('target', axis=1)
y_test = test_data['target']

# Load trained model
import joblib
model = joblib.load('models/trained_model.pkl')

# Run evaluation
evaluator = ModelEvaluator(model, X_test, y_test)
evaluator.predict()
evaluator.calculate_classification_metrics()
evaluator.check_performance_thresholds()
evaluator.print_report()
```

### Example 2: Validate Data Quality Before Training

```python
from scripts.evaluate_data_quality import DataQualityEvaluator
import pandas as pd

# Load training data
df = pd.read_csv('sample_customer_data.csv')

# Run data quality checks
evaluator = DataQualityEvaluator(df, 'Training Data')
evaluator.check_completeness()
evaluator.check_uniqueness(['customer_id'])

# Define business rules
consistency_rules = {
    'purchases_positive': lambda row: row['total_purchases'] >= 0,
    'churn_binary': lambda row: row['churn'] in [0, 1]
}
evaluator.check_consistency(consistency_rules)

evaluator.print_report()

# Fail pipeline if data quality issues found
if len(evaluator.failed) > 0:
    raise Exception(f"Data quality checks failed: {len(evaluator.failed)} issues")
```

## Contributing

When adding new evaluation criteria:

1. Update the appropriate evaluator class
2. Add tests for new functionality
3. Update this documentation
4. Update CI/CD workflows if needed
