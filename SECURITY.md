# Security Policy

## Reporting Security Issues

If you discover a security vulnerability, please email security@company.com instead of using the issue tracker.

## Secret Management

### What Are NOT Secrets (Safe to Commit)
- ✅ Fabric Workspace IDs (resource identifiers)
- ✅ Fabric Lakehouse IDs (resource identifiers)
- ✅ Power BI Report IDs (resource identifiers)
- ✅ Azure Resource Group names
- ✅ Subscription names (not IDs)

**Why?** These are resource identifiers, not authentication credentials. Access requires proper authentication via Service Principal.

### What ARE Secrets (NEVER Commit)
- ❌ Azure Service Principal Client ID (AZURE_CLIENT_ID)
- ❌ Azure Service Principal Client Secret (AZURE_CLIENT_SECRET)
- ❌ Azure Tenant ID (AZURE_TENANT_ID)
- ❌ Azure Subscription ID (AZURE_SUBSCRIPTION_ID)
- ❌ API Keys and Tokens
- ❌ Database connection strings with passwords
- ❌ Private SSH keys
- ❌ TLS/SSL certificates and private keys

## How We Protect Secrets

### 1. GitHub Secrets
All sensitive credentials are stored in GitHub repository secrets:
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `FABRIC_DEV_WORKSPACE_ID`
- `FABRIC_TEST_WORKSPACE_ID`
- `FABRIC_PROD_WORKSPACE_ID`

### 2. Environment Protection
Production deployments require:
- Manual approval
- Change management ticket
- Environment-specific secrets
- Restricted access

### 3. Secret Scanning
- GitHub Secret Scanning: Enabled
- GitGuardian: Configured (see `.gitguardian.yml`)
- Pre-commit hooks: Recommended

### 4. Access Control
- Service Principal has minimum required permissions
- RBAC configured per environment (Dev/Test/Prod)
- Secrets rotated every 90 days

## Fabric Notebook Metadata

Fabric notebooks contain metadata with workspace and lakehouse IDs:
```python
"default_lakehouse": "f1da9f0b-0c17-407e-a5f6-853ae0065c26",
"default_lakehouse_workspace_id": "d44744bc-d9d8-4cd1-a044-bab24399b67d",
```

**These are NOT secrets.** They are:
- Resource identifiers (similar to Azure Resource IDs)
- Required for notebook execution in Fabric
- Useless without proper authentication
- Safe to commit to version control

## Secret Rotation Process

1. **Manual Rotation** (Quarterly):
   ```powershell
   # Rotate Service Principal secret in Azure Portal
   # Then update GitHub secrets
   .\scripts\set-github-secrets.ps1 -Owner "sautalwar" -Repo "nvrcicddemo1" -SecurePrompt
   ```

2. **Automated Rotation** (Planned):
   - Azure Key Vault integration
   - Automated secret renewal
   - GitHub Actions workflow for rotation

## If a Secret is Exposed

### Immediate Actions (Within 1 Hour)
1. ✅ Rotate the exposed secret immediately in Azure Portal
2. ✅ Update GitHub repository secrets
3. ✅ Review Azure Activity Logs for unauthorized access
4. ✅ Notify security team

### Follow-up Actions (Within 24 Hours)
1. Remove secret from Git history:
   ```bash
   git filter-repo --path scripts/set-github-secrets.ps1 --invert-paths
   ```
2. Force push cleaned history (coordinate with team)
3. Document incident in security log
4. Update security procedures if needed

## Best Practices

### For Developers
- ✅ Never hardcode secrets in code
- ✅ Use `.env` files for local development (gitignored)
- ✅ Use `SecureString` in PowerShell for sensitive input
- ✅ Review changes before committing (`git diff`)
- ✅ Run `git secrets --scan` before pushing

### For CI/CD
- ✅ Use GitHub Secrets for all credentials
- ✅ Use `::add-mask::` to hide secrets in logs
- ✅ Minimize secret exposure in workflow logs
- ✅ Use environment protection rules for production

### For Scripts
- ✅ Accept secrets as SecureString parameters
- ✅ Prompt interactively for secrets
- ✅ Never log or echo secret values
- ✅ Clear sensitive variables after use

## Tools and Resources

- **GitHub Secret Scanning**: https://docs.github.com/en/code-security/secret-scanning
- **GitGuardian**: https://www.gitguardian.com/
- **git-secrets**: https://github.com/awslabs/git-secrets
- **Azure Key Vault**: https://azure.microsoft.com/en-us/services/key-vault/
- **GitHub Environments**: https://docs.github.com/en/actions/deployment/environments

## Compliance

This repository follows:
- SOC 2 Type II requirements
- GDPR data protection standards
- Company security policy v2.1
- Microsoft Fabric security best practices

Last updated: January 7, 2026
