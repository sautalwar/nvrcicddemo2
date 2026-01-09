#!/usr/bin/env python3
"""
Validate Jupyter Notebooks for CI/CD pipeline
Checks notebook structure, metadata, and code quality
"""

import json
import sys
from pathlib import Path
from typing import List, Any
import nbformat


class NotebookValidator:
    """Validates Jupyter notebooks for deployment readiness"""

    def __init__(self, notebooks_path: str = "notebooks"):
        self.notebooks_path = Path(notebooks_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self) -> bool:
        """Validate all notebooks in the directory"""
        print("🔍 Starting notebook validation...")
        print(f"📂 Scanning directory: {self.notebooks_path}")

        notebook_files = list(self.notebooks_path.glob("*.ipynb"))

        if not notebook_files:
            self.errors.append(f"No notebooks found in {self.notebooks_path}")
            return False

        print(f"📓 Found {len(notebook_files)} notebook(s)")

        all_valid = True
        for notebook_file in notebook_files:
            print(f"\n📄 Validating: {notebook_file.name}")
            if not self.validate_notebook(notebook_file):
                all_valid = False

        self.print_summary()
        return all_valid

    def validate_notebook(self, notebook_path: Path) -> bool:
        """Validate a single notebook"""
        try:
            # Read and parse notebook
            with open(notebook_path, "r", encoding="utf-8") as f:
                nb = nbformat.read(f, as_version=4)

            # Run validation checks
            checks = [
                self.check_notebook_format(notebook_path, nb),
                self.check_metadata(notebook_path, nb),
                self.check_cells(notebook_path, nb),
                self.check_outputs(notebook_path, nb),
            ]

            return all(checks)

        except json.JSONDecodeError as e:
            self.errors.append(f"{notebook_path.name}: Invalid JSON - {str(e)}")
            return False
        except Exception as e:
            self.errors.append(f"{notebook_path.name}: Validation error - {str(e)}")
            return False

    def check_notebook_format(self, path: Path, nb: Any) -> bool:
        """Check notebook format version"""
        try:
            nbformat.validate(nb)
            print(f"  ✅ Format: Valid (v{nb.nbformat}.{nb.nbformat_minor})")
            return True
        except nbformat.ValidationError as e:
            self.errors.append(f"{path.name}: Format validation failed - {str(e)}")
            print(f"  ❌ Format: Invalid")
            return False

    def check_metadata(self, path: Path, nb: Any) -> bool:
        """Check notebook metadata"""
        metadata = nb.get("metadata", {})

        # Check for kernel info
        if "kernelspec" not in metadata:
            self.warnings.append(f"{path.name}: Missing kernelspec metadata")
            print(f"  ⚠️  Metadata: Missing kernelspec")
            return True  # Warning, not error

        kernel_name = metadata.get("kernelspec", {}).get("name", "unknown")
        print(f"  ✅ Metadata: Kernel = {kernel_name}")
        return True

    def check_cells(self, path: Path, nb: Any) -> bool:
        """Check notebook cells"""
        cells = nb.get("cells", [])

        if not cells:
            self.errors.append(f"{path.name}: Notebook has no cells")
            print(f"  ❌ Cells: Empty notebook")
            return False

        # Count cell types
        code_cells = sum(1 for cell in cells if cell.get("cell_type") == "code")
        markdown_cells = sum(1 for cell in cells if cell.get("cell_type") == "markdown")

        print(
            f"  ✅ Cells: {len(cells)} total ({code_cells} code, {markdown_cells} markdown)"
        )

        # Check for documentation
        if markdown_cells == 0:
            self.warnings.append(
                f"{path.name}: No markdown cells (consider adding documentation)"
            )
            print(f"  ⚠️  Documentation: No markdown cells found")

        # Validate cell structure
        for i, cell in enumerate(cells):
            if "cell_type" not in cell:
                self.errors.append(f"{path.name}: Cell {i} missing cell_type")
                return False
            if "source" not in cell:
                self.errors.append(f"{path.name}: Cell {i} missing source")
                return False

        return True

    def check_outputs(self, path: Path, nb: Any) -> bool:
        """Check if outputs are cleared (best practice for version control)"""
        cells = nb.get("cells", [])
        cells_with_output = 0

        for cell in cells:
            if cell.get("cell_type") == "code":
                outputs = cell.get("outputs", [])
                execution_count = cell.get("execution_count")

                if outputs or execution_count:
                    cells_with_output += 1

        if cells_with_output > 0:
            self.warnings.append(
                f"{path.name}: {cells_with_output} cell(s) have outputs/execution counts "
                "(consider clearing before commit)"
            )
            print(
                f"  ⚠️  Outputs: {cells_with_output} cell(s) have outputs (consider clearing)"
            )
        else:
            print(f"  ✅ Outputs: Clean (no outputs stored)")

        return True

    def print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
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
            print("\n✅ All notebooks passed validation!")
        elif not self.errors:
            print(f"\n✅ All notebooks passed (with {len(self.warnings)} warning(s))")
        else:
            print(f"\n❌ Validation failed with {len(self.errors)} error(s)")

        print("=" * 60)


def main():
    """Main entry point"""
    validator = NotebookValidator("notebooks")

    if validator.validate_all():
        print("\n✅ SUCCESS: All validations passed")
        sys.exit(0)
    else:
        print("\n❌ FAILURE: Validation errors found")
        sys.exit(1)


if __name__ == "__main__":
    main()
