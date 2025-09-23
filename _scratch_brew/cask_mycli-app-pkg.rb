cask "mycli-app-pkg" do
  version "1.0.0"
  
  on_arm do
    sha256 "c91c9261b3a3671015565bfa570918d5062d21f02acd669cdd724f54d45f381b"
    url "https://github.com/naga-nandyala/mycli-app/releases/download/v#{version}/mycli-app-#{version}-arm64.pkg"
  end
  
  on_intel do
    sha256 "5637c56e0a989580ac8ae6a3bde1102db94d31ccea67ff2b64158aee2c358e02"
    url "https://github.com/naga-nandyala/mycli-app/releases/download/v#{version}/mycli-app-#{version}-x86_64.pkg"
  end
  
  name "MyCLI App (PKG Installer)"
  desc "Azure CLI-style tool for cloud operations with native macOS installer"
  homepage "https://github.com/naga-nandyala/mycli-app"
  
  # PKG installer approach
  pkg "mycli-app-#{version}-#{Hardware::CPU.arch}.pkg"
  
  # Binary will be installed to /usr/local/bin/mycli by the pkg installer
  binary "/usr/local/bin/mycli"
  
  # Uninstall options
  uninstall script: {
    executable: "/usr/local/bin/mycli-uninstall.sh",
    sudo:       true
  }
  
  # Postflight verification
  postflight do
    system_command "/usr/local/bin/mycli", args: ["--version"]
  end
  
  # Additional info for users
  caveats <<~EOS
    MyCLI App has been installed system-wide to /usr/local/bin/mycli
    
    Usage:
      mycli --help      # Show help
      mycli --version   # Show version  
      mycli login       # Login to Azure
      mycli status      # Check status
    
    To uninstall:
      sudo mycli-uninstall.sh
    
    Note: This version uses a native macOS .pkg installer for better
    system integration and security compliance.
  EOS
end
