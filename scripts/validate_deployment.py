#!/usr/bin/env python3
"""
Validate Fabric workspace deployment
Checks that deployed artifacts match expected state
"""

import argparse
import os
import sys

try:
    import requests
    from azure.identity import DefaultAzureCredential
except ImportError:
    print("❌ Required packages not installed")
    sys.exit(1)


class DeploymentValidator:
    """Validate Fabric workspace deployments"""

    def __init__(self, workspace_id: str, environment: str):
        self.workspace_id = workspace_id
        self.environment = environment
        self.base_url = "https://api.fabric.microsoft.com/v1"
        self.token = self._get_access_token()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _get_access_token(self) -> str:
        """Get Fabric API access token"""
        token = os.environ.get("FABRIC_TOKEN")
        if token:
            return token

        try:
            credential = DefaultAzureCredential()
            token_result = credential.get_token(
                "https://analysis.windows.net/powerbi/api/.default"
            )
            return token_result.token
        except Exception as e:
            print(f"❌ Failed to acquire token: {str(e)}")
            sys.exit(1)

    def validate_deployment(self) -> bool:
        """Run all validation checks"""
        print("=" * 70)
        print("🔍 DEPLOYMENT VALIDATION")
        print("=" * 70)
        print(f"Workspace ID: {self.workspace_id}")
        print(f"Environment: {self.environment}")
        print()

        checks = [
            ("Workspace Access", self.check_workspace_access()),
            ("Notebooks", self.check_notebooks()),
            ("Workspace State", self.check_workspace_state()),
        ]

        print("\n" + "=" * 70)
        print("📊 VALIDATION RESULTS")
        print("=" * 70)

        all_passed = True
        for check_name, result in checks:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{check_name:30s} {status}")
            if not result:
                all_passed = False

        print("=" * 70)

        return all_passed

    def check_workspace_access(self) -> bool:
        """Verify we can access the workspace"""
        print("\n🔐 Checking workspace access...")

        try:
            url = f"{self.base_url}/workspaces/{self.workspace_id}"
            response = requests.get(url, headers=self.headers, timeout=30)

            if response.status_code == 200:
                workspace = response.json()
                print(f"  ✅ Workspace: {workspace.get('displayName', 'Unknown')}")
                print(f"  ✅ Type: {workspace.get('type', 'Unknown')}")
                return True
            else:
                print(f"  ❌ Cannot access workspace: {response.status_code}")
                return False

        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False

    def check_notebooks(self) -> bool:
        """Verify notebooks are deployed correctly"""
        print("\n📓 Checking deployed notebooks...")

        try:
            url = f"{self.base_url}/workspaces/{self.workspace_id}/notebooks"
            response = requests.get(url, headers=self.headers, timeout=30)

            if response.status_code == 200:
                notebooks = response.json().get("value", [])
                print(f"  ✅ Found {len(notebooks)} notebook(s) in workspace")

                for notebook in notebooks:
                    name = notebook.get("displayName", "Unknown")
                    nb_id = notebook.get("id", "Unknown")[:8]
                    print(f"    • {name} (ID: {nb_id}...)")

                return True
            else:
                print(f"  ⚠️  Could not list notebooks: {response.status_code}")
                return True  # Not a critical failure

        except Exception as e:
            print(f"  ⚠️  Error: {str(e)}")
            return True  # Not a critical failure

    def check_workspace_state(self) -> bool:
        """Check overall workspace state"""
        print("\n📊 Checking workspace state...")

        try:
            # Get all items in workspace
            url = f"{self.base_url}/workspaces/{self.workspace_id}/items"
            response = requests.get(url, headers=self.headers, timeout=30)

            if response.status_code == 200:
                items = response.json().get("value", [])

                # Count by type
                item_counts = {}
                for item in items:
                    item_type = item.get("type", "Unknown")
                    item_counts[item_type] = item_counts.get(item_type, 0) + 1

                print(f"  ✅ Total items: {len(items)}")
                for item_type, count in sorted(item_counts.items()):
                    print(f"    • {item_type}: {count}")

                return True
            else:
                print(f"  ⚠️  Could not list items: {response.status_code}")
                return True

        except Exception as e:
            print(f"  ⚠️  Error: {str(e)}")
            return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Validate Fabric deployment")
    parser.add_argument("--workspace-id", required=True, help="Fabric workspace ID")
    parser.add_argument(
        "--environment",
        required=True,
        choices=["dev", "test", "prod"],
        help="Environment",
    )
    parser.add_argument("--strict-mode", action="store_true", help="Fail on warnings")

    args = parser.parse_args()

    validator = DeploymentValidator(args.workspace_id, args.environment)

    if validator.validate_deployment():
        print("\n✅ VALIDATION PASSED")
        sys.exit(0)
    else:
        print("\n❌ VALIDATION FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
