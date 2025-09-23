cask "mycli-app-pkg" do
  version "1.0.0"
  
  on_arm do
    sha256 "0eed17e14a96766fa72046d6a6bd8d690d40c32e5c9b5a0e68be6b17fb864d6b"
    url "https://github.com/naga-nandyala/mycli-app/releases/download/v#{version}/mycli-app-#{version}-arm64.pkg"
  end
  
  on_intel do
    sha256 "afc1eeee7b8fd46657f3bca306dbaf5bd7f1fec56fdfd7cbf66d83d93d59b6ba"
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
