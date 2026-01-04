# Fabric CI/CD Demo - Quick Reference

## Repository Structure
```
fabric-cicd-demo/
├── .github/workflows/       # CI/CD pipelines
├── notebooks/               # Fabric notebooks
├── pipelines/               # Fabric pipelines  
├── scripts/                 # Deployment scripts
└── config/                  # Environment configs
```

## Demo Flow (30 minutes)

1. **Context** (3 min) - Show repo structure
2. **Local Change** (2 min) - Edit notebook, commit
3. **PR Validation** (3 min) - Open PR, watch checks
4. **Deploy to Dev** (4 min) - Merge, watch deployment
5. **Verify in Fabric** (2 min) - Show changes live
6. **Promotion** (3 min) - Explain Test/Prod gates
7. **Governance** (3 min) - Show audit trail
8. **Q&A** (10 min) - Next steps

## Key Metrics
- **Time savings:** 87% faster (30 min → 4 min)
- **Manual steps:** 15 → 0
- **Deployments:** From error-prone to automated

## Required Secrets
```
AZURE_CLIENT_ID
AZURE_TENANT_ID  
AZURE_SUBSCRIPTION_ID
FABRIC_DEV_WORKSPACE_ID
FABRIC_TEST_WORKSPACE_ID
FABRIC_PROD_WORKSPACE_ID
```

## Local Commands
```bash
# Validate notebooks
python scripts/validate_notebooks.py

# Validate pipelines
python scripts/validate_pipelines.py

# Deploy to Fabric (with credentials)
python scripts/deploy_to_fabric.py \
  --workspace-id <ID> \
  --environment dev \
  --artifact-type notebooks \
  --artifacts-path notebooks/
```

## Deployment Timing
- Dev: 4 minutes (automatic)
- Test: 8 minutes (manual trigger)
- Prod: 15 minutes (gated + backup)
