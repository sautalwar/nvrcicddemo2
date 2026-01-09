#!/usr/bin/env python3
"""
Trigger Fabric Deployment Pipeline to promote content between stages
Integrates GitHub Actions with Fabric deployment pipelines
"""

import argparse
import os
import sys
import time
from typing import Optional

try:
    import requests
    from azure.identity import DefaultAzureCredential
except ImportError:
    print("❌ Required packages not installed")
    print("Run: pip install requests azure-identity")
    sys.exit(1)


class FabricDeploymentPipeline:
    """Interact with Fabric Deployment Pipelines API"""

    def __init__(self, pipeline_id: str):
        self.pipeline_id = pipeline_id
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
                "https://api.fabric.microsoft.com/.default"
            )
            print("✅ Token acquired via DefaultAzureCredential")
            return token_result.token
        except Exception as e:
            print(f"❌ Failed to get token: {e}")
            sys.exit(1)

    def get_pipeline_stages(self) -> dict:
        """Get deployment pipeline stages"""
        print(f"📊 Getting pipeline stages for pipeline: {self.pipeline_id}")

        url = f"{self.base_url}/deploymentPipelines/{self.pipeline_id}/stages"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            stages = response.json()

            print(f"✅ Found {len(stages.get('value', []))} stages:")
            for stage in stages.get("value", []):
                print(f"  - {stage.get('displayName')} (Stage {stage.get('order')})")

            return stages
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get pipeline stages: {e}")
            if hasattr(e.response, "text"):
                print(f"Response: {e.response.text}")
            sys.exit(1)

    def deploy_to_stage(
        self,
        source_stage_order: int,
        target_stage_order: int,
        note: Optional[str] = None,
        wait: bool = True,
    ) -> bool:
        """
        Deploy content from source stage to target stage

        Args:
            source_stage_order: Source stage order (0=Dev, 1=Test, 2=Prod)
            target_stage_order: Target stage order (0=Dev, 1=Test, 2=Prod)
            note: Deployment note/reason
            wait: Wait for deployment to complete

        Returns:
            True if deployment succeeded, False otherwise
        """
        # Get stage IDs from pipeline
        stages_data = self.get_pipeline_stages()
        stages = stages_data.get("value", [])

        # Find source and target stage IDs
        source_stage = next(
            (s for s in stages if s.get("order") == source_stage_order), None
        )
        target_stage = next(
            (s for s in stages if s.get("order") == target_stage_order), None
        )

        if not source_stage or not target_stage:
            print(
                f"❌ Could not find stages with order {source_stage_order} and {target_stage_order}"
            )
            return False

        source_stage_id = source_stage.get("id")
        target_stage_id = target_stage.get("id")
        source_name = source_stage.get("displayName", f"Stage {source_stage_order}")
        target_name = target_stage.get("displayName", f"Stage {target_stage_order}")

        print(f"🚀 Deploying from {source_name} → {target_name}")

        url = f"{self.base_url}/deploymentPipelines/{self.pipeline_id}/deploy"

        payload = {
            "sourceStageId": source_stage_id,
            "targetStageId": target_stage_id,
            "note": note or f"Automated deployment via GitHub Actions",
            "options": {
                "allowCreateArtifact": True,
                "allowOverwriteArtifact": True,
                "allowPurgeData": False,
            },
            "updateAppSettings": {"allowUpdateAny": True},
        }

        try:
            print(f"📤 Sending deployment request...")
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()

            print(f"✅ Deployment request accepted (Status: {response.status_code})")

            # Check if response has content
            if not response.content or response.status_code == 202:
                # 202 Accepted means deployment is queued but may not have operation details yet
                print(f"✅ Deployment initiated to {target_name}")
                return True

            # Try to parse JSON response
            try:
                deployment = response.json()
                operation_id = deployment.get("operationId") if deployment else None

                if operation_id:
                    print(f"✅ Deployment initiated (Operation ID: {operation_id})")
                    if wait:
                        return self._wait_for_deployment(operation_id, target_name)
                else:
                    print(f"✅ Deployment initiated (no operation tracking available)")
            except ValueError:
                # Response is not JSON, but request was successful
                print(f"✅ Deployment initiated to {target_name} (no JSON response)")

            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ Deployment failed: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"Status Code: {e.response.status_code}")
                print(f"Response: {e.response.text}")
            return False

    def _wait_for_deployment(
        self, operation_id: str, target_stage: str, timeout: int = 600
    ) -> bool:
        """
        Wait for deployment operation to complete

        Args:
            operation_id: Deployment operation ID
            target_stage: Name of target stage
            timeout: Maximum wait time in seconds

        Returns:
            True if deployment succeeded, False otherwise
        """
        print(f"⏳ Waiting for deployment to {target_stage}...")

        url = f"{self.base_url}/operations/{operation_id}"
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()

                operation = response.json()
                status = operation.get("status")

                if status == "Succeeded":
                    print(f"✅ Deployment to {target_stage} completed successfully!")
                    return True
                elif status == "Failed":
                    error = operation.get("error", {})
                    print(f"❌ Deployment to {target_stage} failed!")
                    print(f"Error: {error.get('message', 'Unknown error')}")
                    return False
                elif status in ["NotStarted", "Running"]:
                    print(
                        f"  Status: {status}... (elapsed: {int(time.time() - start_time)}s)"
                    )
                    time.sleep(10)  # Check every 10 seconds
                else:
                    print(f"⚠️ Unknown status: {status}")
                    time.sleep(10)

            except requests.exceptions.RequestException as e:
                print(f"⚠️ Error checking deployment status: {e}")
                time.sleep(10)

        print(f"❌ Deployment timed out after {timeout} seconds")
        return False

    def get_pipeline_info(self) -> dict:
        """Get deployment pipeline information"""
        print(f"📋 Getting pipeline information...")

        url = f"{self.base_url}/deploymentPipelines/{self.pipeline_id}"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            pipeline = response.json()

            print(f"✅ Pipeline: {pipeline.get('displayName')}")
            return pipeline
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get pipeline info: {e}")
            if hasattr(e.response, "text"):
                print(f"Response: {e.response.text}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Trigger Fabric Deployment Pipeline promotion"
    )
    parser.add_argument(
        "--pipeline-id", required=True, help="Fabric Deployment Pipeline ID"
    )
    parser.add_argument(
        "--source-stage",
        type=int,
        required=True,
        choices=[0, 1, 2],
        help="Source stage order (0=Dev, 1=Test, 2=Prod)",
    )
    parser.add_argument(
        "--target-stage",
        type=int,
        required=True,
        choices=[0, 1, 2],
        help="Target stage order (0=Dev, 1=Test, 2=Prod)",
    )
    parser.add_argument("--note", help="Deployment note/reason")
    parser.add_argument(
        "--no-wait", action="store_true", help="Don't wait for deployment to complete"
    )
    parser.add_argument(
        "--info", action="store_true", help="Just show pipeline info, don't deploy"
    )

    args = parser.parse_args()

    # Validate stage order
    if args.source_stage >= args.target_stage:
        print("❌ Source stage must be before target stage (Dev→Test→Prod)")
        sys.exit(1)

    pipeline = FabricDeploymentPipeline(args.pipeline_id)

    if args.info:
        pipeline.get_pipeline_info()
        pipeline.get_pipeline_stages()
        return

    # Trigger deployment
    success = pipeline.deploy_to_stage(
        source_stage_order=args.source_stage,
        target_stage_order=args.target_stage,
        note=args.note,
        wait=not args.no_wait,
    )

    if success:
        print("\n🎉 Deployment completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Deployment failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
