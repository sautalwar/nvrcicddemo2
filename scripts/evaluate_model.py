"""
Model Evaluation Framework
Evaluates trained ML models with comprehensive metrics and visualizations
"""

import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    roc_curve, precision_recall_curve
)
from sklearn.model_selection import cross_val_score
import json
from datetime import datetime
import sys


class ModelEvaluator:
    def __init__(self, model, X_test, y_test, X_train=None, y_train=None):
        self.model = model
        self.X_test = X_test
        self.y_test = y_test
        self.X_train = X_train
        self.y_train = y_train
        self.y_pred = None
        self.y_proba = None
        self.metrics = {}
        
    def predict(self):
        """Generate predictions from the model"""
        self.y_pred = self.model.predict(self.X_test)
        if hasattr(self.model, 'predict_proba'):
            self.y_proba = self.model.predict_proba(self.X_test)[:, 1]
        return self
        
    def calculate_classification_metrics(self):
        """Calculate comprehensive classification metrics"""
        if self.y_pred is None:
            self.predict()
            
        self.metrics['accuracy'] = accuracy_score(self.y_test, self.y_pred)
        self.metrics['precision'] = precision_score(self.y_test, self.y_pred, zero_division=0)
        self.metrics['recall'] = recall_score(self.y_test, self.y_pred, zero_division=0)
        self.metrics['f1_score'] = f1_score(self.y_test, self.y_pred, zero_division=0)
        
        if self.y_proba is not None:
            self.metrics['roc_auc'] = roc_auc_score(self.y_test, self.y_proba)
            
        cm = confusion_matrix(self.y_test, self.y_pred)
        self.metrics['confusion_matrix'] = cm.tolist()
        self.metrics['true_negatives'] = int(cm[0, 0])
        self.metrics['false_positives'] = int(cm[0, 1])
        self.metrics['false_negatives'] = int(cm[1, 0])
        self.metrics['true_positives'] = int(cm[1, 1])
        
        return self
        
    def evaluate_model_robustness(self):
        """Evaluate model robustness with cross-validation"""
        if self.X_train is not None and self.y_train is not None:
            cv_scores = cross_val_score(self.model, self.X_train, self.y_train, cv=5, scoring='accuracy')
            self.metrics['cv_scores'] = cv_scores.tolist()
            self.metrics['cv_mean'] = float(cv_scores.mean())
            self.metrics['cv_std'] = float(cv_scores.std())
        return self
        
    def check_performance_thresholds(self, thresholds=None):
        """Check if model meets minimum performance thresholds"""
        if thresholds is None:
            thresholds = {
                'accuracy': 0.70,
                'precision': 0.65,
                'recall': 0.60,
                'f1_score': 0.65
            }
            
        passed_checks = {}
        failed_checks = {}
        
        for metric, threshold in thresholds.items():
            if metric in self.metrics:
                actual = self.metrics[metric]
                passed = actual >= threshold
                check_result = {
                    'threshold': threshold,
                    'actual': actual,
                    'passed': passed,
                    'gap': actual - threshold
                }
                
                if passed:
                    passed_checks[metric] = check_result
                else:
                    failed_checks[metric] = check_result
                    
        self.metrics['threshold_checks'] = {
            'passed': passed_checks,
            'failed': failed_checks,
            'all_passed': len(failed_checks) == 0
        }
        
        return self
        
    def generate_report(self):
        """Generate comprehensive evaluation report"""
        report = {
            'evaluation_timestamp': datetime.now().isoformat(),
            'model_type': type(self.model).__name__,
            'test_samples': len(self.X_test),
            'metrics': self.metrics
        }
        
        return report
        
    def print_report(self):
        """Print formatted evaluation report"""
        print("\n" + "=" * 70)
        print("MODEL EVALUATION REPORT")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70 + "\n")
        
        print(f"Model Type: {type(self.model).__name__}")
        print(f"Test Samples: {len(self.X_test)}")
        print()
        
        print("CLASSIFICATION METRICS")
        print("-" * 70)
        print(f"  Accuracy:  {self.metrics.get('accuracy', 0):.4f}")
        print(f"  Precision: {self.metrics.get('precision', 0):.4f}")
        print(f"  Recall:    {self.metrics.get('recall', 0):.4f}")
        print(f"  F1 Score:  {self.metrics.get('f1_score', 0):.4f}")
        if 'roc_auc' in self.metrics:
            print(f"  ROC AUC:   {self.metrics['roc_auc']:.4f}")
        print()
        
        print("CONFUSION MATRIX")
        print("-" * 70)
        cm = np.array(self.metrics['confusion_matrix'])
        print(f"  True Negatives:  {self.metrics['true_negatives']}")
        print(f"  False Positives: {self.metrics['false_positives']}")
        print(f"  False Negatives: {self.metrics['false_negatives']}")
        print(f"  True Positives:  {self.metrics['true_positives']}")
        print()
        
        if 'cv_scores' in self.metrics:
            print("CROSS-VALIDATION RESULTS")
            print("-" * 70)
            print(f"  Mean CV Score: {self.metrics['cv_mean']:.4f}")
            print(f"  Std Dev:       {self.metrics['cv_std']:.4f}")
            print()
            
        if 'threshold_checks' in self.metrics:
            checks = self.metrics['threshold_checks']
            print("PERFORMANCE THRESHOLD CHECKS")
            print("-" * 70)
            
            for metric, result in checks['passed'].items():
                print(f"  ✅ {metric:12s}: {result['actual']:.4f} (threshold: {result['threshold']:.4f})")
                
            for metric, result in checks['failed'].items():
                print(f"  ❌ {metric:12s}: {result['actual']:.4f} (threshold: {result['threshold']:.4f}, gap: {result['gap']:.4f})")
            
            print()
            if checks['all_passed']:
                print("  ✅ All performance thresholds passed!")
            else:
                print(f"  ⚠️  {len(checks['failed'])} threshold(s) failed!")
            print()
            
        print("=" * 70)
        
        return self
        
    def save_report(self, filepath='evaluation_report.json'):
        """Save evaluation report to JSON file"""
        report = self.generate_report()
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"✅ Evaluation report saved to: {filepath}")
        return self


def evaluate_model_from_file(model_path, test_data_path):
    """Load and evaluate a saved model"""
    import joblib
    
    model = joblib.load(model_path)
    test_data = pd.read_csv(test_data_path)
    
    X_test = test_data.drop('target', axis=1)
    y_test = test_data['target']
    
    evaluator = ModelEvaluator(model, X_test, y_test)
    evaluator.predict()
    evaluator.calculate_classification_metrics()
    evaluator.check_performance_thresholds()
    evaluator.print_report()
    
    return evaluator


if __name__ == "__main__":
    print("Model Evaluation Framework")
    print("Import this module to use ModelEvaluator class")
    print("\nExample usage:")
    print("  from evaluate_model import ModelEvaluator")
    print("  evaluator = ModelEvaluator(model, X_test, y_test)")
    print("  evaluator.predict().calculate_classification_metrics()")
    print("  evaluator.check_performance_thresholds().print_report()")
