# Broker-Based Authentication in MyCliApp

## Overview

MyCliApp now supports broker-based authentication, providing enhanced security and user experience through integration with system-level authentication mechanisms like Windows Hello and Microsoft Authenticator.

## What is Broker Authentication?

Broker authentication leverages external identity brokers to handle authentication flows. This provides several benefits:

- **Enhanced Security**: Utilizes biometric authentication (fingerprint, face recognition)
- **Seamless Experience**: Integrates with system authentication mechanisms
- **Centralized Management**: Leverages organizational identity policies
- **Multi-Factor Authentication**: Built-in support for MFA through authenticator apps

## Supported Authentication Methods

### 1. Windows Hello for Business
- **Biometric Authentication**: Fingerprint, facial recognition, iris scanning
- **PIN-based Authentication**: Secure PIN authentication
- **Hardware Security**: Leverages TPM (Trusted Platform Module) when available

### 2. Microsoft Authenticator
- **Push Notifications**: Receive authentication requests on your mobile device
- **Time-based Codes**: Generate TOTP codes for authentication
- **Passwordless Authentication**: Authenticate without passwords

### 3. Device Code Flow
- **Cross-platform Support**: Works on any device with a web browser
- **Limited Connectivity**: Useful when direct browser access is restricted

## Usage Examples

### Basic Broker Authentication
```bash
# Use broker-based authentication (recommended on Windows)
mycli login --use-broker

# Specify a tenant with broker authentication
mycli login --use-broker --tenant your-tenant-id
```

### Device Code Flow
```bash
# Use device code flow (good for remote/headless scenarios)
mycli login --use-device-code

# Device code with specific tenant
mycli login --use-device-code --tenant your-tenant-id
```

### Traditional Browser Authentication
```bash
# Standard browser-based authentication
mycli login

# With specific tenant
mycli login --tenant your-tenant-id
```

## Platform Support

### Windows (Full Support)
- ✅ Windows Hello for Business
- ✅ Microsoft Authenticator
- ✅ Broker token caching
- ✅ Device code flow
- ✅ Browser authentication

### macOS/Linux (Limited Support)
- ❌ Windows Hello (Windows-specific)
- ✅ Microsoft Authenticator (through browser)
- ❌ Native broker integration
- ✅ Device code flow (recommended)
- ✅ Browser authentication

## Commands

### Check Broker Capabilities
```bash
# View broker authentication information
mycli broker
```

### View Authentication Status
```bash
# Check current authentication status
mycli whoami

# System status including broker support
mycli status

# Account information
mycli account
```

### Logout
```bash
# Logout from current session
mycli logout
```

## Configuration

Authentication state is stored in `~/.mycli/config.json` and includes:
- Authentication status
- User information
- Tenant details
- Authentication method used
- Broker capabilities (when applicable)

## Troubleshooting

### Broker Authentication Issues

1. **Windows Hello not working**:
   - Ensure Windows Hello is set up in Windows Settings
   - Verify biometric devices are configured
   - Try running the CLI as administrator

2. **Microsoft Authenticator issues**:
   - Ensure the Authenticator app is installed and configured
   - Check that your organization allows authenticator-based authentication
   - Verify network connectivity

3. **Token caching issues**:
   - Clear the authentication state: `mycli logout`
   - Try device code flow as an alternative: `mycli login --use-device-code`

### General Authentication Issues

1. **Azure SDK not available**:
   ```bash
   pip install azure-identity azure-mgmt-core azure-core msal
   ```

2. **Permission issues**:
   - Ensure you have proper permissions in the Azure tenant
   - Verify your account is not blocked or disabled

3. **Network connectivity**:
   - Check firewall settings
   - Verify access to `login.microsoftonline.com`

## Security Considerations

### Broker Authentication Security
- Uses hardware-backed security when available (TPM)
- Tokens are encrypted and stored securely by the OS
- Biometric data never leaves the device
- Supports organizational conditional access policies

### Best Practices
1. **Use broker authentication on Windows** for enhanced security
2. **Enable MFA** in your Azure AD tenant
3. **Regularly review** authentication logs
4. **Use device code flow** on shared or public computers
5. **Logout** when using shared devices

## Implementation Details

The broker authentication implementation:

1. **Detection**: Automatically detects platform capabilities
2. **Fallback**: Gracefully falls back to browser authentication if broker fails
3. **Caching**: Leverages system token cache for seamless re-authentication
4. **Error Handling**: Provides detailed error messages and troubleshooting guidance

### Authentication Flow
```
User Request → Platform Detection → Credential Selection → Authentication → Token Storage → Access Granted
```

### Supported Credential Types
- `InteractiveBrowserCredential` (with broker support)
- `SharedTokenCacheCredential` (cached broker tokens)
- `DeviceCodeCredential` (device code flow)
- `AzureCliCredential` (Azure CLI integration)

## Future Enhancements

Planned improvements for 2025-2026:
- [x] **Windows Hello Integration** - Completed in v1.0.0
- [x] **Microsoft Authenticator Support** - Completed in v1.0.0
- [ ] Support for FIDO2/WebAuthn security keys
- [ ] Integration with Azure AD Conditional Access policies
- [ ] Enhanced logging and audit capabilities
- [ ] Support for certificate-based authentication
- [ ] macOS Keychain integration for broker-like experience
- [ ] **Passkey Support** - Modern passwordless authentication
- [ ] **Azure Code Signing Integration** - For signed executable distribution
- [ ] **Enterprise SSO Integration** - Seamless corporate authentication

### Modern Authentication Trends (2025)

#### Passwordless Authentication
- **Windows Hello for Business** - Biometric and PIN-based authentication
- **FIDO2/WebAuthn** - Hardware security keys
- **Passkeys** - Cross-platform passwordless experience
- **Microsoft Authenticator** - Phone-based authentication

#### Zero Trust Architecture
- **Conditional Access** - Policy-based access control
- **Device Compliance** - Trusted device requirements
- **Risk-based Authentication** - Adaptive security measures
- **Continuous Authentication** - Session monitoring and validation
