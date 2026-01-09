#!/usr/bin/env python3
"""
Schema Change Detection for Power BI Reports
Detects breaking changes in notebook output schemas that could break downstream reports.

Usage:
    python detect_schema_changes.py --notebook model_training.Notebook/notebook-content.py
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple


class SchemaChangeDetector:
    """Detects breaking schema changes in notebook outputs"""

    # Define which changes are BREAKING vs. SAFE
    BREAKING_CHANGES = [
        "column_removed",
        "column_renamed",
        "data_type_changed",
        "column_made_nullable",
    ]

    SAFE_CHANGES = ["column_added", "column_made_non_nullable"]

    def __init__(self, notebook_path: str):
        self.notebook_path = Path(notebook_path)
        self.schema_file = self.notebook_path.parent / "output_schema.json"

    def extract_schema_from_notebook(self) -> Dict:
        """
        Extract schema from notebook code by finding DataFrame writes

        Simple approach: Look for comments that define schema
        Example in notebook:
            # SCHEMA: customers
            # COLUMNS: customer_id (string), name (string), lifetime_value (double)
        """
        with open(self.notebook_path, "r", encoding="utf-8") as f:
            content = f.read()

        schemas = {}
        current_table = None

        for line in content.split("\n"):
            # Find schema definitions in comments
            if "# SCHEMA:" in line:
                current_table = line.split("# SCHEMA:")[1].strip()
                schemas[current_table] = {"columns": {}}

            elif "# COLUMNS:" in line and current_table:
                # Parse: customer_id (string), name (string), lifetime_value (double)
                columns_def = line.split("# COLUMNS:")[1].strip()
                for col_def in columns_def.split(","):
                    col_def = col_def.strip()
                    if "(" in col_def and ")" in col_def:
                        col_name = col_def.split("(")[0].strip()
                        col_type = col_def.split("(")[1].split(")")[0].strip()
                        nullable = "nullable" in col_def.lower()

                        schemas[current_table]["columns"][col_name] = {
                            "type": col_type,
                            "nullable": nullable,
                        }

        return schemas

    def load_previous_schema(self) -> Dict:
        """Load schema from previous commit (saved in output_schema.json)"""
        if not self.schema_file.exists():
            return {}

        with open(self.schema_file, "r") as f:
            return json.load(f)

    def save_current_schema(self, schema: Dict):
        """Save current schema for future comparison"""
        with open(self.schema_file, "w") as f:
            json.dump(schema, f, indent=2)

    def detect_changes(self, old_schema: Dict, new_schema: Dict) -> List[Dict]:
        """Compare old and new schemas, return list of changes"""
        changes = []

        # Check each table
        for table_name in set(list(old_schema.keys()) + list(new_schema.keys())):
            old_cols = old_schema.get(table_name, {}).get("columns", {})
            new_cols = new_schema.get(table_name, {}).get("columns", {})

            # Detect removed columns
            for col_name in old_cols:
                if col_name not in new_cols:
                    changes.append(
                        {
                            "type": "column_removed",
                            "severity": "BREAKING",
                            "table": table_name,
                            "column": col_name,
                            "message": f"Column '{col_name}' was removed from table '{table_name}'",
                        }
                    )

            # Detect added columns
            for col_name in new_cols:
                if col_name not in old_cols:
                    changes.append(
                        {
                            "type": "column_added",
                            "severity": "SAFE",
                            "table": table_name,
                            "column": col_name,
                            "message": f"Column '{col_name}' was added to table '{table_name}'",
                        }
                    )

            # Detect type changes
            for col_name in old_cols:
                if col_name in new_cols:
                    old_type = old_cols[col_name]["type"]
                    new_type = new_cols[col_name]["type"]

                    if old_type != new_type:
                        changes.append(
                            {
                                "type": "data_type_changed",
                                "severity": "BREAKING",
                                "table": table_name,
                                "column": col_name,
                                "message": f"Column '{col_name}' type changed from {old_type} to {new_type}",
                            }
                        )

                    # Detect nullable changes
                    old_nullable = old_cols[col_name].get("nullable", False)
                    new_nullable = new_cols[col_name].get("nullable", False)

                    if old_nullable != new_nullable:
                        if new_nullable and not old_nullable:
                            changes.append(
                                {
                                    "type": "column_made_nullable",
                                    "severity": "BREAKING",
                                    "table": table_name,
                                    "column": col_name,
                                    "message": f"Column '{col_name}' changed from non-nullable to nullable",
                                }
                            )
                        else:
                            changes.append(
                                {
                                    "type": "column_made_non_nullable",
                                    "severity": "SAFE",
                                    "table": table_name,
                                    "column": col_name,
                                    "message": f"Column '{col_name}' changed from nullable to non-nullable",
                                }
                            )

        return changes

    def run(self) -> Tuple[bool, List[Dict]]:
        """
        Run schema change detection

        Returns:
            (has_breaking_changes: bool, all_changes: List[Dict])
        """
        print(f"🔍 Analyzing schema changes in: {self.notebook_path}")

        # Extract schema from current notebook code
        current_schema = self.extract_schema_from_notebook()

        if not current_schema:
            print("⚠️  No schema definitions found in notebook")
            print("   Add schema comments like:")
            print("   # SCHEMA: customers")
            print("   # COLUMNS: customer_id (string), name (string)")
            return False, []

        # Load previous schema
        previous_schema = self.load_previous_schema()

        if not previous_schema:
            print("ℹ️  No previous schema found. Saving current schema as baseline...")
            self.save_current_schema(current_schema)
            return False, []

        # Detect changes
        changes = self.detect_changes(previous_schema, current_schema)

        if not changes:
            print("✅ No schema changes detected")
            return False, []

        # Classify changes
        breaking_changes = [c for c in changes if c["severity"] == "BREAKING"]
        safe_changes = [c for c in changes if c["severity"] == "SAFE"]

        # Report findings
        if breaking_changes:
            print("\n🚨 BREAKING CHANGES DETECTED (will break Power BI reports):")
            for change in breaking_changes:
                print(f"   ❌ {change['message']}")

        if safe_changes:
            print("\n✅ Safe changes (won't break existing reports):")
            for change in safe_changes:
                print(f"   ✓ {change['message']}")

        # Save current schema for next comparison
        self.save_current_schema(current_schema)

        return len(breaking_changes) > 0, changes


def main():
    parser = argparse.ArgumentParser(description="Detect schema changes in notebooks")
    parser.add_argument("--notebook", required=True, help="Path to notebook file")
    parser.add_argument(
        "--fail-on-breaking",
        action="store_true",
        help="Exit with error code if breaking changes detected",
    )

    args = parser.parse_args()

    detector = SchemaChangeDetector(args.notebook)
    has_breaking_changes, changes = detector.run()

    if has_breaking_changes and args.fail_on_breaking:
        print("\n❌ VALIDATION FAILED: Breaking schema changes detected")
        print("   Power BI reports may break. Please review changes.")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
