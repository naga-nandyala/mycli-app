# Homebrew Formula Auto-Update Setup

This document explains how to set up automatic Homebrew formula updates for the `homebrew-mycli-app` repository.

## Problem

The GitHub Actions workflow `update-homebrew-formula.yml` needs to push changes to the separate `naga-nandyala/homebrew-mycli-app` repository. The default `GITHUB_TOKEN` doesn't have permissions to push to external repositories.

## Solution

Create a Personal Access Token (PAT) with appropriate permissions.

## Setup Steps

### 1. Create Personal Access Token

1. Go to **GitHub Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
   - Direct link: https://github.com/settings/tokens

2. Click **"Generate new token"** → **"Generate new token (classic)"**

3. Configure the token:
   - **Note**: `Homebrew Tap Auto-Update for mycli-app`
   - **Expiration**: Choose your preferred expiration (90 days, 1 year, or no expiration)
   - **Scopes**: Select the following:
     - ✅ **`repo`** (Full control of private repositories)
       - This includes: `repo:status`, `repo_deployment`, `public_repo`, `repo:invite`, `security_events`

4. Click **"Generate token"**

5. **Important**: Copy the token immediately - you won't be able to see it again!

### 2. Add Token to Repository Secrets

1. Go to the **main repository**: `naga-nandyala/mycli-app`

2. Navigate to **Settings** → **Secrets and variables** → **Actions**

3. Click **"New repository secret"**

4. Add the secret:
   - **Name**: `HOMEBREW_TAP_TOKEN`
   - **Secret**: Paste the Personal Access Token you created

5. Click **"Add secret"**

### 3. Verify Setup

The workflow will now use the PAT for cross-repository operations:

```yaml
# In .github/workflows/update-homebrew-formula.yml
- name: Checkout Homebrew tap repository
  uses: actions/checkout@v4
  with:
    repository: naga-nandyala/homebrew-mycli-app
    token: ${{ secrets.HOMEBREW_TAP_TOKEN || secrets.GITHUB_TOKEN }}
    path: homebrew-tap
```

### 4. Test the Workflow

You can test the setup by:

1. **Manual trigger**: Go to **Actions** → **Update Homebrew Formula** → **Run workflow**
2. **Release trigger**: Publish a new release (the workflow runs automatically)

## Troubleshooting

### Permission Denied (403)

If you see this error:
```
remote: Permission to naga-nandyala/homebrew-mycli-app.git denied to github-actions[bot].
fatal: unable to access 'https://github.com/naga-nandyala/homebrew-mycli-app/': The requested URL returned error: 403
```

**Solutions:**
1. Verify the `HOMEBREW_TAP_TOKEN` secret exists and is correctly named
2. Check that the PAT has `repo` scope permissions
3. Ensure the PAT hasn't expired
4. Verify you have write access to the `homebrew-mycli-app` repository

### Token Not Found

If the `HOMEBREW_TAP_TOKEN` secret doesn't exist, the workflow falls back to `GITHUB_TOKEN`, which has limited permissions for cross-repository operations.

### Repository Access

Make sure the Personal Access Token has access to the `naga-nandyala/homebrew-mycli-app` repository. If it's a private repository, the token needs appropriate permissions.

## Security Best Practices

1. **Minimal Scope**: Only grant the `repo` scope - don't add unnecessary permissions
2. **Regular Rotation**: Set a reasonable expiration date and rotate tokens periodically
3. **Monitor Usage**: Check the token usage in GitHub Settings if needed
4. **Revoke if Compromised**: If the token is compromised, revoke it immediately and create a new one

## Workflow Overview

Once set up, the workflow automatically:

1. **Triggers** on new releases or manual dispatch
2. **Downloads** release assets (ARM64 and x86_64 tarballs)
3. **Calculates** SHA256 hashes for both architectures
4. **Updates** the Homebrew formula with new version and hashes
5. **Commits** and pushes changes to the tap repository
6. **Notifies** of success or failure

Users can then install the updated version with:
```bash
brew install naga-nandyala/mycli-app/mycli-app
```
