"""
Data Quality Evaluation Framework
Validates data quality across multiple dimensions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import sys


class DataQualityEvaluator:
    def __init__(self, dataframe, data_name="Dataset"):
        self.df = dataframe
        self.data_name = data_name
        self.checks = {}
        self.passed = []
        self.failed = []
        
    def check_completeness(self, null_threshold=0.05):
        """Check data completeness (missing values)"""
        results = {}
        
        for column in self.df.columns:
            null_count = self.df[column].isnull().sum()
            null_pct = null_count / len(self.df)
            
            passed = null_pct <= null_threshold
            results[column] = {
                'null_count': int(null_count),
                'null_percentage': float(null_pct),
                'threshold': null_threshold,
                'passed': passed
            }
            
            if passed:
                self.passed.append(f"Completeness: {column}")
            else:
                self.failed.append(f"Completeness: {column} ({null_pct:.2%} > {null_threshold:.2%})")
                
        self.checks['completeness'] = results
        return self
        
    def check_uniqueness(self, unique_columns):
        """Check uniqueness for specified columns"""
        results = {}
        
        for column in unique_columns:
            if column not in self.df.columns:
                continue
                
            total_rows = len(self.df)
            unique_rows = self.df[column].nunique()
            duplicate_count = total_rows - unique_rows
            
            passed = duplicate_count == 0
            results[column] = {
                'total_rows': total_rows,
                'unique_values': unique_rows,
                'duplicate_count': int(duplicate_count),
                'passed': passed
            }
            
            if passed:
                self.passed.append(f"Uniqueness: {column}")
            else:
                self.failed.append(f"Uniqueness: {column} ({duplicate_count} duplicates)")
                
        self.checks['uniqueness'] = results
        return self
        
    def check_consistency(self, consistency_rules):
        """Check data consistency based on business rules"""
        results = {}
        
        for rule_name, rule_func in consistency_rules.items():
            try:
                violations = self.df[~self.df.apply(rule_func, axis=1)]
                violation_count = len(violations)
                
                passed = violation_count == 0
                results[rule_name] = {
                    'violations': int(violation_count),
                    'violation_percentage': float(violation_count / len(self.df)),
                    'passed': passed
                }
                
                if passed:
                    self.passed.append(f"Consistency: {rule_name}")
                else:
                    self.failed.append(f"Consistency: {rule_name} ({violation_count} violations)")
            except Exception as e:
                results[rule_name] = {
                    'error': str(e),
                    'passed': False
                }
                self.failed.append(f"Consistency: {rule_name} (error: {str(e)})")
                
        self.checks['consistency'] = results
        return self
        
    def check_accuracy(self, value_ranges):
        """Check if values are within expected ranges"""
        results = {}
        
        for column, range_spec in value_ranges.items():
            if column not in self.df.columns:
                continue
                
            min_val = range_spec.get('min', -np.inf)
            max_val = range_spec.get('max', np.inf)
            
            out_of_range = self.df[
                (self.df[column] < min_val) | (self.df[column] > max_val)
            ]
            violation_count = len(out_of_range)
            
            passed = violation_count == 0
            results[column] = {
                'expected_range': f"[{min_val}, {max_val}]",
                'actual_min': float(self.df[column].min()),
                'actual_max': float(self.df[column].max()),
                'violations': int(violation_count),
                'passed': passed
            }
            
            if passed:
                self.passed.append(f"Accuracy: {column}")
            else:
                self.failed.append(f"Accuracy: {column} ({violation_count} out of range)")
                
        self.checks['accuracy'] = results
        return self
        
    def check_timeliness(self, date_column, max_age_days=30):
        """Check data freshness"""
        if date_column not in self.df.columns:
            return self
            
        try:
            latest_date = pd.to_datetime(self.df[date_column]).max()
            age_days = (datetime.now() - latest_date).days
            
            passed = age_days <= max_age_days
            self.checks['timeliness'] = {
                'latest_date': latest_date.isoformat(),
                'age_days': int(age_days),
                'max_age_days': max_age_days,
                'passed': passed
            }
            
            if passed:
                self.passed.append("Timeliness check")
            else:
                self.failed.append(f"Timeliness: Data is {age_days} days old (max: {max_age_days})")
        except Exception as e:
            self.checks['timeliness'] = {
                'error': str(e),
                'passed': False
            }
            self.failed.append(f"Timeliness: Error - {str(e)}")
            
        return self
        
    def check_validity(self, validation_rules):
        """Check data validity with custom validation functions"""
        results = {}
        
        for column, validator in validation_rules.items():
            if column not in self.df.columns:
                continue
                
            try:
                valid_mask = self.df[column].apply(validator)
                invalid_count = (~valid_mask).sum()
                
                passed = invalid_count == 0
                results[column] = {
                    'invalid_count': int(invalid_count),
                    'invalid_percentage': float(invalid_count / len(self.df)),
                    'passed': passed
                }
                
                if passed:
                    self.passed.append(f"Validity: {column}")
                else:
                    self.failed.append(f"Validity: {column} ({invalid_count} invalid)")
            except Exception as e:
                results[column] = {
                    'error': str(e),
                    'passed': False
                }
                self.failed.append(f"Validity: {column} (error: {str(e)})")
                
        self.checks['validity'] = results
        return self
        
    def generate_report(self):
        """Generate comprehensive data quality report"""
        total_checks = len(self.passed) + len(self.failed)
        
        report = {
            'evaluation_timestamp': datetime.now().isoformat(),
            'data_name': self.data_name,
            'dataset_shape': self.df.shape,
            'total_checks': total_checks,
            'passed_checks': len(self.passed),
            'failed_checks': len(self.failed),
            'success_rate': len(self.passed) / total_checks if total_checks > 0 else 0,
            'checks': self.checks,
            'passed': self.passed,
            'failed': self.failed
        }
        
        return report
        
    def print_report(self):
        """Print formatted data quality report"""
        print("\n" + "=" * 70)
        print("DATA QUALITY EVALUATION REPORT")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70 + "\n")
        
        print(f"Dataset: {self.data_name}")
        print(f"Shape: {self.df.shape[0]} rows × {self.df.shape[1]} columns")
        print()
        
        if 'completeness' in self.checks:
            print("COMPLETENESS CHECKS")
            print("-" * 70)
            for column, result in self.checks['completeness'].items():
                status = "✅" if result['passed'] else "❌"
                print(f"  {status} {column:30s}: {result['null_percentage']:.2%} nulls (threshold: {result['threshold']:.2%})")
            print()
            
        if 'uniqueness' in self.checks:
            print("UNIQUENESS CHECKS")
            print("-" * 70)
            for column, result in self.checks['uniqueness'].items():
                status = "✅" if result['passed'] else "❌"
                print(f"  {status} {column:30s}: {result['duplicate_count']} duplicates")
            print()
            
        if 'consistency' in self.checks:
            print("CONSISTENCY CHECKS")
            print("-" * 70)
            for rule, result in self.checks['consistency'].items():
                status = "✅" if result['passed'] else "❌"
                violations = result.get('violations', 'N/A')
                print(f"  {status} {rule:30s}: {violations} violations")
            print()
            
        if 'accuracy' in self.checks:
            print("ACCURACY CHECKS")
            print("-" * 70)
            for column, result in self.checks['accuracy'].items():
                status = "✅" if result['passed'] else "❌"
                print(f"  {status} {column:30s}: Range {result['expected_range']}, Violations: {result['violations']}")
            print()
            
        if 'timeliness' in self.checks:
            print("TIMELINESS CHECKS")
            print("-" * 70)
            result = self.checks['timeliness']
            status = "✅" if result['passed'] else "❌"
            if 'age_days' in result:
                print(f"  {status} Data Age: {result['age_days']} days (max: {result['max_age_days']})")
            print()
            
        if 'validity' in self.checks:
            print("VALIDITY CHECKS")
            print("-" * 70)
            for column, result in self.checks['validity'].items():
                status = "✅" if result['passed'] else "❌"
                invalid = result.get('invalid_count', 'N/A')
                print(f"  {status} {column:30s}: {invalid} invalid values")
            print()
            
        print("SUMMARY")
        print("-" * 70)
        total = len(self.passed) + len(self.failed)
        success_rate = (len(self.passed) / total * 100) if total > 0 else 0
        print(f"  Total Checks: {total}")
        print(f"  Passed: {len(self.passed)}")
        print(f"  Failed: {len(self.failed)}")
        print(f"  Success Rate: {success_rate:.1f}%")
        print()
        
        if len(self.failed) == 0:
            print("  ✅ All data quality checks passed!")
        else:
            print(f"  ⚠️  {len(self.failed)} check(s) failed!")
            
        print("=" * 70)
        
        return self
        
    def save_report(self, filepath='data_quality_report.json'):
        """Save data quality report to JSON file"""
        report = self.generate_report()
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"✅ Data quality report saved to: {filepath}")
        return self


if __name__ == "__main__":
    print("Data Quality Evaluation Framework")
    print("Import this module to use DataQualityEvaluator class")
    print("\nExample usage:")
    print("  from evaluate_data_quality import DataQualityEvaluator")
    print("  evaluator = DataQualityEvaluator(df, 'Customer Data')")
    print("  evaluator.check_completeness().check_uniqueness(['customer_id'])")
    print("  evaluator.print_report()")
