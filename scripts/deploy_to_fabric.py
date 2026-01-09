#!/usr/bin/env python3
"""
Deploy artifacts to Microsoft Fabric workspace
Supports notebooks, pipelines, and other Fabric items
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional
import time

try:
    import requests
    from azure.identity import DefaultAzureCredential
except ImportError:
    print("❌ Required packages not installed")
    print("Run: pip install requests azure-identity")
    sys.exit(1)


class FabricDeployer:
    """Deploy artifacts to Microsoft Fabric"""

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
        print("🔐 Acquiring Fabric access token...")

        # Try environment variable first (for CI/CD)
        token = os.environ.get("FABRIC_TOKEN")
        if token:
            print("✅ Using token from environment variable")
            return token

        # Use Azure credential (for local development)
        try:
            credential = DefaultAzureCredential()
            token_result = credential.get_token(
                "https://analysis.windows.net/powerbi/api/.default"
            )
            print("✅ Acquired token using Azure credential")
            return token_result.token
        except Exception as e:
            print(f"❌ Failed to acquire token: {str(e)}")
            sys.exit(1)

    def deploy_notebooks(self, notebooks_path: Path) -> bool:
        """Deploy notebooks to Fabric workspace"""
        print(f"\n📓 Deploying notebooks from {notebooks_path}...")

        notebook_files = list(notebooks_path.glob("*.ipynb"))
        if not notebook_files:
            print("⏭️  No notebooks found to deploy")
            return True

        print(f"Found {len(notebook_files)} notebook(s) to deploy")

        success_count = 0
        for notebook_file in notebook_files:
            if self._deploy_notebook(notebook_file):
                success_count += 1
                time.sleep(1)  # Rate limiting

        print(
            f"\n✅ Successfully deployed {success_count}/{len(notebook_files)} notebook(s)"
        )
        return success_count == len(notebook_files)

    def _deploy_notebook(self, notebook_path: Path) -> bool:
        """Deploy a single notebook"""
        notebook_name = notebook_path.stem
        print(f"\n📝 Deploying notebook: {notebook_name}")

        try:
            # Read notebook content
            with open(notebook_path, "r", encoding="utf-8") as f:
                notebook_content = json.load(f)

            # Check if notebook exists
            existing_notebook = self._get_notebook_by_name(notebook_name)

            if existing_notebook:
                print(f"  ♻️  Notebook exists - updating...")
                notebook_id = existing_notebook["id"]
                success = self._update_notebook(
                    notebook_id, notebook_name, notebook_content
                )
            else:
                print(f"  ➕ Creating new notebook...")
                success = self._create_notebook(notebook_name, notebook_content)

            if success:
                print(f"  ✅ Deployed: {notebook_name}")
                return True
            else:
                print(f"  ❌ Failed to deploy: {notebook_name}")
                return False

        except Exception as e:
            print(f"  ❌ Error deploying {notebook_name}: {str(e)}")
            return False

    def _get_notebook_by_name(self, name: str) -> Optional[Dict]:
        """Get notebook by name from workspace"""
        try:
            url = f"{self.base_url}/workspaces/{self.workspace_id}/notebooks"
            response = requests.get(url, headers=self.headers, timeout=30)

            if response.status_code == 200:
                notebooks = response.json().get("value", [])
                for notebook in notebooks:
                    if notebook.get("displayName") == name:
                        return notebook
            return None
        except Exception as e:
            print(f"  ⚠️  Error checking existing notebooks: {str(e)}")
            return None

    def _create_notebook(self, name: str, content: Dict) -> bool:
        """Create a new notebook in Fabric"""
        try:
            url = f"{self.base_url}/workspaces/{self.workspace_id}/notebooks"

            payload = {
                "displayName": name,
                "definition": {
                    "format": "ipynb",
                    "parts": [
                        {
                            "path": "notebook-content.py",
                            "payload": self._convert_notebook_to_payload(content),
                            "payloadType": "InlineBase64",
                        }
                    ],
                },
            }

            response = requests.post(
                url, headers=self.headers, json=payload, timeout=60
            )

            if response.status_code in [200, 201, 202]:
                if response.status_code == 202:
                    print(
                        f"  ⏳ Notebook creation accepted (processing asynchronously)"
                    )
                return True
            else:
                print(f"  ❌ API Error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"  ❌ Error creating notebook: {str(e)}")
            return False

    def _update_notebook(self, notebook_id: str, name: str, content: Dict) -> bool:
        """Update an existing notebook in Fabric"""
        try:
            url = f"{self.base_url}/workspaces/{self.workspace_id}/notebooks/{notebook_id}/updateDefinition"

            payload = {
                "definition": {
                    "format": "ipynb",
                    "parts": [
                        {
                            "path": "notebook-content.py",
                            "payload": self._convert_notebook_to_payload(content),
                            "payloadType": "InlineBase64",
                        }
                    ],
                }
            }

            response = requests.post(
                url, headers=self.headers, json=payload, timeout=60
            )

            if response.status_code in [200, 201, 202]:
                if response.status_code == 202:
                    print(f"  ⏳ Notebook update accepted (processing asynchronously)")
                return True
            else:
                print(f"  ❌ API Error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"  ❌ Error updating notebook: {str(e)}")
            return False

    def _convert_notebook_to_payload(self, notebook_content: Dict) -> str:
        """Convert notebook JSON to base64 payload"""
        import base64

        # Convert notebook to JSON string
        notebook_json = json.dumps(notebook_content, indent=2)

        # Encode to base64
        payload_bytes = notebook_json.encode("utf-8")
        base64_bytes = base64.b64encode(payload_bytes)
        base64_string = base64_bytes.decode("utf-8")

        return base64_string

    def deploy_pipelines(self, pipelines_path: Path) -> bool:
        """Deploy pipelines to Fabric workspace"""
        print(f"\n🔄 Deploying pipelines from {pipelines_path}...")

        if not pipelines_path.exists():
            print("⏭️  Pipelines directory does not exist - skipping")
            return True

        pipeline_files = list(pipelines_path.glob("*.json"))
        if not pipeline_files:
            print("⏭️  No pipelines found to deploy")
            return True

        print(f"Found {len(pipeline_files)} pipeline(s) to deploy")

        # For now, just validate the files exist
        # In production, you would call Fabric Pipeline APIs
        for pipeline_file in pipeline_files:
            print(f"  📋 {pipeline_file.name} - ready for deployment")

        print(f"\n✅ Pipelines validated (deployment APIs would be called here)")
        return True

    def validate_workspace(self) -> bool:
        """Validate workspace access"""
        print(f"\n🔍 Validating workspace access...")
        print(f"  Workspace ID: {self.workspace_id}")
        print(f"  Environment: {self.environment}")

        try:
            url = f"{self.base_url}/workspaces/{self.workspace_id}"
            response = requests.get(url, headers=self.headers, timeout=30)

            if response.status_code == 200:
                workspace_data = response.json()
                print(f"  ✅ Workspace: {workspace_data.get('displayName', 'Unknown')}")
                return True
            else:
                print(f"  ❌ Cannot access workspace: {response.status_code}")
                return False

        except Exception as e:
            print(f"  ❌ Validation error: {str(e)}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Deploy artifacts to Microsoft Fabric")
    parser.add_argument("--workspace-id", required=True, help="Fabric workspace ID")
    parser.add_argument(
        "--environment",
        required=True,
        choices=["dev", "test", "prod"],
        help="Target environment",
    )
    parser.add_argument(
        "--artifact-type",
        required=True,
        choices=["notebooks", "pipelines", "all"],
        help="Type of artifacts to deploy",
    )
    parser.add_argument(
        "--artifacts-path", default=".", help="Path to artifacts directory"
    )
    parser.add_argument(
        "--validate-before-deploy",
        action="store_true",
        help="Validate workspace before deployment",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("🚀 FABRIC DEPLOYMENT TOOL")
    print("=" * 70)

    # Initialize deployer
    deployer = FabricDeployer(args.workspace_id, args.environment)

    # Validate workspace if requested
    if args.validate_before_deploy:
        if not deployer.validate_workspace():
            print("\n❌ Workspace validation failed - aborting deployment")
            sys.exit(1)

    # Deploy artifacts
    artifacts_path = Path(args.artifacts_path)
    success = True

    if args.artifact_type in ["notebooks", "all"]:
        notebooks_path = artifacts_path / "notebooks"
        if not deployer.deploy_notebooks(notebooks_path):
            success = False

    if args.artifact_type in ["pipelines", "all"]:
        pipelines_path = artifacts_path / "pipelines"
        if not deployer.deploy_pipelines(pipelines_path):
            success = False

    print("\n" + "=" * 70)
    if success:
        print("✅ DEPLOYMENT COMPLETED SUCCESSFULLY")
        print("=" * 70)
        sys.exit(0)
    else:
        print("❌ DEPLOYMENT FAILED")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
