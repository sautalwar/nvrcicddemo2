#!/usr/bin/env python3
"""
Validate Fabric Pipeline JSON files
Checks JSON schema and structure
"""

import json
import sys
from pathlib import Path
from typing import List


class PipelineValidator:
    """Validates Fabric pipeline JSON files"""
    
    def __init__(self, pipelines_path: str = "pipelines"):
        self.pipelines_path = Path(pipelines_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_all(self) -> bool:
        """Validate all pipeline files"""
        print("🔍 Starting pipeline validation...")
        print(f"📂 Scanning directory: {self.pipelines_path}")
        
        if not self.pipelines_path.exists():
            print(f"⏭️  Directory {self.pipelines_path} does not exist - skipping")
            return True
        
        pipeline_files = list(self.pipelines_path.glob("*.json"))
        
        if not pipeline_files:
            print(f"ℹ️  No pipeline JSON files found in {self.pipelines_path}")
            return True
        
        print(f"📋 Found {len(pipeline_files)} pipeline file(s)")
        
        all_valid = True
        for pipeline_file in pipeline_files:
            print(f"\n📄 Validating: {pipeline_file.name}")
            if not self.validate_pipeline(pipeline_file):
                all_valid = False
        
        self.print_summary()
        return all_valid
    
    def validate_pipeline(self, pipeline_path: Path) -> bool:
        """Validate a single pipeline JSON file"""
        try:
            # Read and parse JSON
            with open(pipeline_path, 'r', encoding='utf-8') as f:
                pipeline_data = json.load(f)
            
            print(f"  ✅ JSON: Valid syntax")
            
            # Check required fields for Fabric pipelines
            if not self.check_pipeline_structure(pipeline_path, pipeline_data):
                return False
            
            return True
            
        except json.JSONDecodeError as e:
            self.errors.append(f"{pipeline_path.name}: Invalid JSON - {str(e)}")
            print(f"  ❌ JSON: Invalid syntax")
            return False
        except Exception as e:
            self.errors.append(f"{pipeline_path.name}: Validation error - {str(e)}")
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def check_pipeline_structure(self, path: Path, data: dict) -> bool:
        """Check pipeline structure and required fields"""
        
        # Check for name
        if 'name' in data:
            print(f"  ✅ Name: {data['name']}")
        else:
            self.warnings.append(f"{path.name}: Missing 'name' field")
            print(f"  ⚠️  Name: Not specified")
        
        # Check for activities (common in Fabric pipelines)
        if 'properties' in data:
            properties = data['properties']
            
            if 'activities' in properties:
                activities = properties['activities']
                print(f"  ✅ Activities: {len(activities)} activity(ies)")
                
                # Validate each activity
                for i, activity in enumerate(activities):
                    if 'name' not in activity:
                        self.errors.append(f"{path.name}: Activity {i} missing 'name'")
                        return False
                    if 'type' not in activity:
                        self.errors.append(f"{path.name}: Activity {i} missing 'type'")
                        return False
            else:
                self.warnings.append(f"{path.name}: No activities defined")
                print(f"  ⚠️  Activities: None defined")
        
        return True
    
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 60)
        print("📊 PIPELINE VALIDATION SUMMARY")
        print("=" * 60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All pipelines passed validation!")
        elif not self.errors:
            print(f"\n✅ All pipelines passed (with {len(self.warnings)} warning(s))")
        else:
            print(f"\n❌ Validation failed with {len(self.errors)} error(s)")
        
        print("=" * 60)


def main():
    """Main entry point"""
    validator = PipelineValidator("pipelines")
    
    if validator.validate_all():
        print("\n✅ SUCCESS: Pipeline validation passed")
        sys.exit(0)
    else:
        print("\n❌ FAILURE: Pipeline validation errors found")
        sys.exit(1)


if __name__ == "__main__":
    main()
