# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "f1da9f0b-0c17-407e-a5f6-853ae0065c26",
# META       "default_lakehouse_name": "customer_data_lakehouse",
# META       "default_lakehouse_workspace_id": "d44744bc-d9d8-4cd1-a044-bab24399b67d",
# META       "known_lakehouses": [
# META         {
# META           "id": "f1da9f0b-0c17-407e-a5f6-853ae0065c26"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

# Import libraries
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import mlflow
import mlflow.sklearn

print("✅ Libraries imported successfully today")
print(f"📅 Training started at: {datetime.now()}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df = spark.read.format("csv").option("header","true").load("Files/sample_customer_data.csv")
# df now is a Spark DataFrame containing CSV data from "Files/sample_customer_data.csv".
display(df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Load training data from Lakehouse
print("📂 Loading data from Lakehouse...")

data = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load("Files/sample_customer_data.csv") \
    .toPandas()

print(f"✅ Loaded {len(data)} customer records from Lakehouse")
print(f"\n📊 Dataset shape: {data.shape}")
print(f"\n🎯 Churn distribution:\n{data['churn'].value_counts()}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df = spark.read.format("csv").option("header","true").load("Files/sample_customer_data.csv")
# df now is a Spark DataFrame containing CSV data from "Files/sample_customer_data.csv".
display(df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Feature engineering
print("🔧 Engineering features...")

# Prevent division by zero for new customers (customer_age_days = 0)
data['purchase_frequency'] = data['total_purchases'] / np.maximum(data['customer_age_days'] / 30, 1)
data['engagement_score'] = (data['total_purchases'] * data['avg_purchase_value']) / np.maximum(data['customer_age_days'], 1)
data['recency_score'] = 1 / (data['days_since_last_purchase'] + 1)

feature_columns = [
    'total_purchases', 'avg_purchase_value', 'days_since_last_purchase',
    'customer_age_days', 'support_tickets', 'purchase_frequency',
    'engagement_score', 'recency_score'
]

X = data[feature_columns]
y = data['churn']

print(f"✅ Features prepared: {len(feature_columns)} features")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"📊 Training set: {len(X_train)} samples")
print(f"📊 Test set: {len(X_test)} samples")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Model training with MLflow tracking
print("\n🤖 Training Random Forest model...")

mlflow.set_experiment("NVR_Customer_Churn_Prediction")

with mlflow.start_run(run_name=f"rf_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
    # Model parameters
    params = {
        'n_estimators': 100,
        'max_depth': 10,
        'min_samples_split': 5,
        'random_state': 42
    }
    
    # Log parameters
    mlflow.log_params(params)
    
    # Train model
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)
    
    print("✅ Model training completed")
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    # Log metrics
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("f1_score", f1)
    
    # Log model
    mlflow.sklearn.log_model(model, "random_forest_model")
    
    print("\n📊 Model Performance Metrics:")
    print("=" * 40)
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1 Score:  {f1:.4f}")
    print("=" * 40)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Feature importance analysis
print("\n🔍 Feature Importance:")
print("=" * 40)

feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

for idx, row in feature_importance.iterrows():
    print(f"  {row['feature']:30s} {row['importance']:.4f}")

print("=" * 40)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Model validation summary
print("\n✅ Model Training Pipeline Completed")
print("=" * 50)
print(f"  Model Type: Random Forest Classifier")
print(f"  Training Samples: {len(X_train)}")
print(f"  Test Samples: {len(X_test)}")
print(f"  Features: {len(feature_columns)}")
print(f"  Model Accuracy: {accuracy:.2%}")
print(f"  Completed at: {datetime.now()}")
print("=" * 50)
print("\n🚀 Model ready for deployment!")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
