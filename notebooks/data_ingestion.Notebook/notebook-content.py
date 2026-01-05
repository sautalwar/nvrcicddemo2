# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   }
# META }

# CELL ********************

# Import required libraries
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit, current_timestamp

print("✅ Libraries imported successfully")
print(f"📅 Pipeline started at: {datetime.now()}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Initialize Spark session
spark = SparkSession.builder \
    .appName("NVR-DataIngestion") \
    .getOrCreate()

print(f"✅ Spark session initialized: {spark.version}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Configuration
BRONZE_PATH = "Files/bronze/customer_transactions"
SILVER_PATH = "Files/silver/customer_transactions_clean"

print(f"📂 Bronze Layer: {BRONZE_PATH}")
print(f"📂 Silver Layer: {SILVER_PATH}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Read data from Bronze layer
try:
    df_bronze = spark.read \
        .format("delta") \
        .load(BRONZE_PATH)
    
    print(f"✅ Successfully read {df_bronze.count()} records from Bronze layer")
    print("\n📊 Schema:")
    df_bronze.printSchema()
except Exception as e:
    print(f"❌ Error reading Bronze layer: {str(e)}")
    raise

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Data Quality Checks
print("🔍 Running data quality checks...")

# Check for nulls in critical columns
null_checks = df_bronze.select(
    [col(c).isNull().cast("int").alias(c) for c in df_bronze.columns]
).groupBy().sum().collect()[0].asDict()

print("\nNull value counts:")
for col_name, null_count in null_checks.items():
    if null_count > 0:
        print(f"  ⚠️  {col_name}: {null_count} nulls")
    else:
        print(f"  ✅ {col_name}: No nulls")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Data Transformations
print("\n🔧 Applying transformations...")

df_silver = df_bronze \
    .filter(col("transaction_amount") > 0) \
    .filter(col("customer_id").isNotNull()) \
    .withColumn("processing_timestamp", current_timestamp()) \
    .withColumn("data_quality_flag", 
                when(col("transaction_amount") > 10000, "high_value")
                .when(col("transaction_amount") < 10, "low_value")
                .otherwise("normal"))

print(f"✅ Transformations applied. Records after filtering: {df_silver.count()}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Write to Silver layer
try:
    df_silver.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .save(SILVER_PATH)
    
    print(f"✅ Successfully wrote {df_silver.count()} records to Silver layer")
    print(f"📂 Location: {SILVER_PATH}")
except Exception as e:
    print(f"❌ Error writing to Silver layer: {str(e)}")
    raise

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Summary Statistics
print("\n📊 Pipeline Summary:")
print("=" * 50)

summary = df_silver.groupBy("data_quality_flag").count().collect()
for row in summary:
    print(f"  {row['data_quality_flag']}: {row['count']} records")

print("\n" + "=" * 50)
print(f"✅ Pipeline completed successfully at {datetime.now()}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
