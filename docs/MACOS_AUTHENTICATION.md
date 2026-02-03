# macOS Authentication Guide

This document explains how authentication works in mycli-app on macOS, with a focus on broker authentication using macOS Keychain and native authentication dialogs.

## Sources

This documentation is based on official sources:

- **MSAL Python Source Code**: [AzureAD/microsoft-authentication-library-for-python](https://github.com/AzureAD/microsoft-authentication-library-for-python)
- **Broker Test Documentation**: [tests/broker-test.py](https://github.com/AzureAD/microsoft-authentication-library-for-python/blob/main/tests/broker-test.py) - States: *"If you are on a mac device, install CP (Company Portal), login an account in CP and finish the MDM process."*
- **PublicClientApplication Docstring**: [msal/application.py](https://github.com/AzureAD/microsoft-authentication-library-for-python/blob/main/msal/application.py#L2000-L2009) - Documents redirect URIs and requirements per platform

## Table of Contents

- [Overview](#overview)
- [Authentication Methods](#authentication-methods)
- [Broker Authentication on macOS](#broker-authentication-on-macos)
- [How It Works (Code Flow)](#how-it-works-code-flow)
- [Requirements](#requirements)
- [Troubleshooting](#troubleshooting)

---

## Overview

mycli-app supports multiple Azure authentication methods on macOS:

| Method | Command | Description |
|--------|---------|-------------|
| **Browser** | `mycli login` | Opens browser for OAuth login |
| **Broker** | `mycli login --use-broker` | Uses native macOS broker (Touch ID, Keychain) |
| **Force Broker** | `mycli login --force-broker` | Native broker only, no fallback |
| **Device Code** | `mycli login --use-device-code` | For headless/SSH scenarios |

---

## Authentication Methods

### 1. Browser Authentication (Default)

```bash
mycli login
```

- Opens default browser for Microsoft login
- Uses `InteractiveBrowserCredential` from Azure Identity SDK
- Works on all platforms
- No special setup required

### 2. Broker Authentication

```bash
mycli login --use-broker
```

- Uses native macOS broker via `pymsalruntime`
- Enables Touch ID, Face ID, and Keychain integration
- Falls back to browser if broker fails
- **Requires Python 3.12+** for proper pymsalruntime support

### 3. Force Broker (No Fallback)

```bash
mycli login --force-broker
```

- Same as `--use-broker` but fails if broker unavailable
- Useful for enforcing strong authentication policies

### 4. Device Code Flow

```bash
mycli login --use-device-code
``

- Displays a code to enter at microsoft.com/devicelogin
- Useful for SSH sessions or headless environments

---

## Broker Authentication on macOS

### What is Broker Authentication?

Broker authentication uses the **Microsoft Authentication Library (MSAL)** with `pymsalruntime` native binary to provide secure authentication via macOS system services.

**What the broker actually uses** (confirmed by testing):
- **macOS Keychain** - Secure credential storage (✅ verified working)
- **Native authentication popup** - System dialog for login

**Additional capabilities** (require additional setup):
- **Company Portal + MDM enrollment** - Enhanced broker features per MSAL docs
- **Touch ID / Face ID** - May require Keychain biometric settings or SSO Extension
- **SSO Extension** - Enterprise deployment via MDM for seamless SSO

### Key Components

**Application Layer:**

| Component | Description |
| --------- | ----------- |
| `cli.py` | Entry point with `get_macos_broker_credential()` |
| ↓ | |
| **MSAL** (`msal>=1.20`) | `PublicClientApplication(enable_broker_on_mac=True)` |
| ↓ | |
| **pymsalruntime** (`0.18.x`) | Native binary that communicates with macOS broker |

**macOS System Services:**

| Service | Status |
| ------- | ------ |
| ✅ Keychain Services | Credential storage - **CONFIRMED WORKING** |
| ◯ LocalAuthentication.framework | Touch ID - OPTIONAL |
| ◯ Microsoft Enterprise SSO Extension | Via MDM - OPTIONAL |
| ◯ Company Portal | Enhances broker - OPTIONAL |

> **Note from MSAL source**: Per [broker-test.py](https://github.com/AzureAD/microsoft-authentication-library-for-python/blob/main/tests/broker-test.py):
> *"If you are on a mac device, install CP (Company Portal), login an account in CP and finish the MDM process."*

### Python Version Requirement

> ⚠️ **Important**: Broker authentication requires **Python 3.12+**

The `pymsalruntime` wheel for Python 3.9 has known issues with macOS broker authentication (error `-42000`). Always use Python 3.12:

```bash
# Check your Python version
python3 --version

# Create venv with Python 3.12
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[azure,broker]"
```

---

## How It Works (Code Flow)

### 1. Entry Point: `login` Command

```python
# cli.py - login command
@cli.command()
@click.option('--use-broker', is_flag=True, help='Use broker-based authentication')
@click.option('--force-broker', is_flag=True, help='Force broker, no fallback')
def login(use_broker, force_broker, ...):
    if use_broker or force_broker:
        authenticate_user_with_broker(tenant_id, force_broker=force_broker)
```

### 2. Broker Authentication Flow

```python
# cli.py - authenticate_user_with_broker()
def authenticate_user_with_broker(tenant_id=None, force_broker=False):
    # Get broker info (checks platform capabilities)
    broker_info = get_broker_info()
    
    # Get credential via native broker
    credential, auth_method = get_azure_credential(tenant_id, use_broker=True)
    
    # Acquire token
    token = credential.get_token("https://management.azure.com/.default")
```

### 3. macOS-Specific Broker Logic

```python
# cli.py - get_macos_broker_credential()
def get_macos_broker_credential(tenant_id=None):
    import msal
    
    # Create MSAL app with macOS broker enabled
    app = msal.PublicClientApplication(
        client_id="04b07795-8ddb-461a-bbee-02f9e1bf7b46",  # Azure CLI client ID
        authority=f"https://login.microsoftonline.com/{tenant_id or 'common'}",
        enable_broker_on_mac=True,  # 🔑 Key setting for macOS
    )
    
    # Try 1: Silent auth from cache
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(
            scopes=["https://management.azure.com/.default"],
            account=accounts[0]
        )
        if result and "access_token" in result:
            return result, "broker_cached"
    
    # Try 2: Interactive broker (Touch ID popup)
    result = app.acquire_token_interactive(
        scopes=["https://management.azure.com/.default"],
        parent_window_handle=app.CONSOLE_WINDOW_HANDLE,
        enable_broker=True,
        prompt="select_account",
    )
    
    if result and "access_token" in result:
        return result, "broker_interactive"
```

### 4. Credential Wrapper

The MSAL result is wrapped in an Azure SDK-compatible credential:

```python
# cli.py - MSALBrokerCredential wrapper
class MSALBrokerCredential:
    def __init__(self, msal_result):
        self.msal_result = msal_result

    def get_token(self, *scopes, **kwargs):
        expires_on = int(time.time()) + self.msal_result.get("expires_in", 3600)
        return AccessToken(self.msal_result["access_token"], expires_on)
```

### 5. Fallback Chain

If broker fails, the code falls back gracefully:

```
get_macos_broker_credential() fallback chain:
═══════════════════════════════════════════════

1. acquire_token_silent() [cached tokens]
   │
   ├── Success → "broker_cached" ✅
   │
   └── Fail → Try interactive...
   
2. acquire_token_interactive(CONSOLE_WINDOW_HANDLE, enable_broker=True)
   │
   ├── Success → "broker_interactive" ✅
   │
   └── Fail → Try without console window handle...
   
3. acquire_token_interactive(enable_broker=True)
   │
   ├── Success → "broker_interactive" ✅
   │
   └── Fail → Try without broker...
   
4. acquire_token_interactive() [no broker flag]
   │
   ├── Success → "browser_interactive" ⚠️ (fallback)
   │
   └── Fail → Return to get_azure_credential()...

get_azure_credential() additional fallbacks:
═══════════════════════════════════════════════

5. SharedTokenCacheCredential()
   │
   ├── Success → "broker_cache" ✅
   │
   └── Fail → Last resort...
   
6. InteractiveBrowserCredential(enable_broker_on_mac=True)
   │
   └── Returns → "browser_with_broker" ⚠️ (browser fallback)
```

### 6. Auth Method Return Values

| Return Value | Meaning | User Experience |
|--------------|---------|-----------------|
| `broker_cached` | Silent auth from cache | No popup, instant |
| `broker_interactive` | Native broker popup | macOS auth dialog |
| `browser_interactive` | Browser opened (broker failed) | Browser opens |
| `broker_cache` | SharedTokenCacheCredential | Uses cached tokens |
| `browser_with_broker` | Browser with broker hints | Browser opens |

---

## Cache Management

### Clear Cached Tokens

```bash
# Clear all cached tokens including broker cache
mycli clear-cache --all
```

### How `clear_broker_cache()` Works on macOS

```python
# cli.py - clear_broker_cache()
app = msal.PublicClientApplication(
    client_id="04b07795-8ddb-461a-bbee-02f9e1bf7b46",
    authority="https://login.microsoftonline.com/common",
    enable_broker_on_mac=True,  # macOS-specific
)

# Remove all cached accounts
accounts = app.get_accounts()
for account in accounts:
    app.remove_account(account)
```

---

## Requirements

### Python Packages

```toml
# pyproject.toml
[project.optional-dependencies]
broker = [
    "azure-identity>=1.12.0",
    "azure-mgmt-core>=1.3.0", 
    "azure-core>=1.24.0",
    "msal[broker]>=1.20.0,<2",  # Includes pymsalruntime
]
```

Install with:
```bash
pip install -e ".[broker]"
# or
pip install "msal[broker]>=1.20,<2"
```

### System Requirements

| Requirement | Details |
|-------------|---------|
| macOS | 10.15 (Catalina) or later |
| Python | **3.12+** (3.9 has pymsalruntime issues) |
| Touch ID | Enabled in System Settings (optional) |
| Company Portal | From App Store (optional, enhances broker) |
| SSO Extension | Deployed via MDM (optional, for enterprise SSO) |

### Optional: Microsoft Company Portal

For enhanced broker features:

1. Install **Microsoft Company Portal** from the Mac App Store
2. Sign in with your Microsoft account
3. This enables additional broker capabilities

### Optional: Enterprise SSO Extension

For enterprise environments, IT can deploy the Microsoft Enterprise SSO Extension via MDM (Jamf, Intune, etc.) for seamless SSO across all Microsoft apps.

---

## Troubleshooting

### Error: `-42000` (Status_Unexpected)

```
Broker authentication failed: ... Error code: -42000
```

**Cause**: Wrong Python version. The `pymsalruntime` wheel for Python 3.9 has a bug that causes this error on macOS.

**Solution**: Use Python 3.12+

```bash
# Check your current Python version
python --version

# If it's not 3.12+, recreate your venv:
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[broker]"
```

This is the **most common cause** of the `-42000` error. After switching to Python 3.12, broker authentication should work.

### Error: `parent_window_handle is required`

**Cause**: MSAL console window handle issue on some macOS versions.

**Solution**: The code automatically falls back. If persistent:

```bash
mycli login --use-device-code
```

### Error: `msal[broker] not available`

**Cause**: pymsalruntime not installed.

**Solution**:

```bash
pip install "msal[broker]>=1.20,<2"
```

### Broker works with Homebrew but not local dev

**Cause**: Different Python versions.

**Solution**: Ensure local venv uses Python 3.12:
```bash
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[azure,broker]"
```

### Check broker availability

```bash
mycli broker
```

Expected output:
```text
🔐 Broker Authentication Information:

Platform Support:
  Operating System: posix
  Broker Support: Available

Available Authentication Methods:
  • macOS Keychain
  • Touch ID / Face ID (availability depends on system config)
  • Microsoft Authenticator app (if installed)
```

> **Note**: The `get_broker_info()` function reports *potential* capabilities. Actual availability depends on:
> - Company Portal installation and MDM enrollment
> - System biometric settings
> - SSO Extension deployment (for enterprise SSO)

---

## Code Reference

| Function | File | Purpose |
|----------|------|---------|
| `get_macos_broker_credential()` | `cli.py:188` | macOS-specific MSAL broker auth |
| `get_azure_credential()` | `cli.py:296` | Main credential factory |
| `get_broker_info()` | `cli.py:383` | Platform capability detection |
| `authenticate_user_with_broker()` | `cli.py:418` | High-level broker auth flow |
| `clear_broker_cache()` | `cli.py:85` | Clear cached broker tokens |

---

## See Also

- [MSAL Python Broker Documentation](https://github.com/AzureAD/microsoft-authentication-library-for-python/wiki/Using-the-broker-on-macOS)
- [Azure Identity SDK](https://learn.microsoft.com/en-us/python/api/azure-identity/)
- [pymsalruntime](https://pypi.org/project/pymsalruntime/)
