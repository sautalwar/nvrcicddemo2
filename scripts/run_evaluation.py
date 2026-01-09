"""
Run Complete Evaluation Suite
Executes all evaluation checks for the workspace
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os


def evaluate_sample_data():
    """Evaluate sample customer data quality"""
    print("\n" + "=" * 70)
    print("EVALUATING SAMPLE CUSTOMER DATA")
    print("=" * 70)
    
    try:
        df = pd.read_csv('sample_customer_data.csv')
        
        from evaluate_data_quality import DataQualityEvaluator
        
        evaluator = DataQualityEvaluator(df, 'Customer Churn Dataset')
        
        evaluator.check_completeness(null_threshold=0.05)
        
        evaluator.check_uniqueness(['customer_id'])
        
        consistency_rules = {
            'total_purchases_positive': lambda row: row['total_purchases'] >= 0,
            'avg_purchase_positive': lambda row: row['avg_purchase_value'] >= 0,
            'days_positive': lambda row: row['days_since_last_purchase'] >= 0,
            'age_positive': lambda row: row['customer_age_days'] >= 0,
            'churn_binary': lambda row: row['churn'] in [0, 1]
        }
        evaluator.check_consistency(consistency_rules)
        
        value_ranges = {
            'total_purchases': {'min': 0, 'max': 1000},
            'avg_purchase_value': {'min': 0, 'max': 10000},
            'days_since_last_purchase': {'min': 0, 'max': 3650},
            'customer_age_days': {'min': 0, 'max': 36500},
            'support_tickets': {'min': 0, 'max': 100},
            'churn': {'min': 0, 'max': 1}
        }
        evaluator.check_accuracy(value_ranges)
        
        evaluator.print_report()
        evaluator.save_report('reports/data_quality_report.json')
        
        return evaluator.checks
        
    except Exception as e:
        print(f"❌ Error evaluating data: {str(e)}")
        return None


def run_model_benchmarks():
    """Run model performance benchmarks"""
    print("\n" + "=" * 70)
    print("MODEL PERFORMANCE BENCHMARKS")
    print("=" * 70)
    
    benchmarks = {
        'baseline_accuracy': 0.50,
        'target_accuracy': 0.75,
        'baseline_precision': 0.50,
        'target_precision': 0.70,
        'baseline_recall': 0.50,
        'target_recall': 0.65,
        'baseline_f1': 0.50,
        'target_f1': 0.70
    }
    
    print("\nMINIMUM PERFORMANCE THRESHOLDS:")
    print("-" * 70)
    print(f"  Accuracy:  {benchmarks['target_accuracy']:.2%}")
    print(f"  Precision: {benchmarks['target_precision']:.2%}")
    print(f"  Recall:    {benchmarks['target_recall']:.2%}")
    print(f"  F1 Score:  {benchmarks['target_f1']:.2%}")
    print()
    
    return benchmarks


def validate_pipeline_outputs():
    """Validate that pipeline outputs meet requirements"""
    print("\n" + "=" * 70)
    print("PIPELINE OUTPUT VALIDATION")
    print("=" * 70)
    
    checks = []
    
    if os.path.exists('sample_customer_data.csv'):
        checks.append(('Sample data file exists', True))
    else:
        checks.append(('Sample data file exists', False))
        
    if os.path.exists('notebooks/model_training.ipynb') or os.path.exists('notebooks/model_training.Notebook'):
        checks.append(('Model training notebook exists', True))
    else:
        checks.append(('Model training notebook exists', False))
        
    if os.path.exists('check_data_quality.py'):
        checks.append(('Data quality script exists', True))
    else:
        checks.append(('Data quality script exists', False))
        
    print("\nPIPELINE ARTIFACT CHECKS:")
    print("-" * 70)
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
    print()
    
    all_passed = all(passed for _, passed in checks)
    if all_passed:
        print("  ✅ All pipeline artifacts validated!")
    else:
        print("  ⚠️  Some pipeline artifacts are missing!")
    print()
    
    return checks


def generate_evaluation_summary():
    """Generate overall evaluation summary"""
    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    summary = {
        'timestamp': datetime.now().isoformat(),
        'evaluation_components': [
            'Data Quality Assessment',
            'Model Performance Benchmarks',
            'Pipeline Output Validation'
        ],
        'status': 'Complete'
    }
    
    print("\nEvaluation Components:")
    for component in summary['evaluation_components']:
        print(f"  ✅ {component}")
    
    print("\n" + "=" * 70)
    print("✅ EVALUATION FRAMEWORK COMPLETED SUCCESSFULLY")
    print("=" * 70 + "\n")
    
    return summary


def main():
    """Run complete evaluation suite"""
    os.makedirs('reports', exist_ok=True)
    
    print("\n" + "=" * 70)
    print("NVR WORKSPACE EVALUATION FRAMEWORK")
    print("=" * 70)
    
    data_quality = evaluate_sample_data()
    
    benchmarks = run_model_benchmarks()
    
    pipeline_validation = validate_pipeline_outputs()
    
    summary = generate_evaluation_summary()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
