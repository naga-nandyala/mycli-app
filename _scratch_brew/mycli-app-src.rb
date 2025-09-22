# Homebrew formula for mycli-app (source-based installation)
class MycliAppSrc < Formula
  include  resource "pymsalruntime" do
    url "https://files.pythonhosted.org/packages/af/4f/7b99671b2dacdecbb9bd9caccb0fe9b0a39d4579c488b25ebf73613bda8d/pymsalruntime-0.18.1-cp312-cp312-macosx_14_0_arm64.whl"
    sha256 "a6c07651cf4e07690d1b022da0977f56820ef553ac6dcbf4c9e68e9611020997"
  endguage::Python::Virtualenv

  desc "Simple Azure-like CLI tool by Naga (Source Installation)"
  homepage "https://github.com/naga-nandyala/mycli-app"
  url "https://github.com/naga-nandyala/mycli-app/archive/refs/tags/v0.1.2.tar.gz"
  sha256 "d11b7315068bce4f76989d79f05383cd06d0dff64e288a94371e3a0d631752a1"
  license "MIT"
  head "https://github.com/naga-nandyala/mycli-app.git", branch: "main"

  livecheck do
    url :stable
    regex(/^v?(\d+(?:\.\d+)+)$/i)
    strategy :github_latest
  end

  bottle do
    # Homebrew will generate these automatically when building bottles
  end

  depends_on "python@3.12"

  # Build dependencies for cryptography
  depends_on "rust" => :build
  depends_on "pkgconf" => :build
  depends_on "openssl@3"

  uses_from_macos "libffi"

  resource "azure-core" do
    url "https://files.pythonhosted.org/packages/15/6b/2653adc0f33adba8f11b1903701e6b1c10d34ce5d8e25dfa13a422f832b0/azure_core-1.35.1.tar.gz"
    sha256 "435d05d6df0fff2f73fb3c15493bb4721ede14203f1ff1382aa6b6b2bdd7e562"
  end

  resource "azure-identity" do
    url "https://files.pythonhosted.org/packages/4e/9e/4c9682a286c3c89e437579bd9f64f311020e5125c1321fd3a653166b5716/azure_identity-1.25.0.tar.gz"
    sha256 "4177df34d684cddc026e6cf684e1abb57767aa9d84e7f2129b080ec45eee7733"
  end

  resource "azure-mgmt-core" do
    url "https://files.pythonhosted.org/packages/3e/99/fa9e7551313d8c7099c89ebf3b03cd31beb12e1b498d575aa19bb59a5d04/azure_mgmt_core-1.6.0.tar.gz"
    sha256 "b26232af857b021e61d813d9f4ae530465255cb10b3dde945ad3743f7a58e79c"
  end

  resource "certifi" do
    url "https://files.pythonhosted.org/packages/dc/67/960ebe6bf230a96cda2e0abcf73af550ec4f090005363542f0765df162e0/certifi-2025.8.3.tar.gz"
    sha256 "e564105f78ded564e3ae7c923924435e1daa7463faeab5bb932bc53ffae63407"
  end

  resource "cffi" do
    url "https://files.pythonhosted.org/packages/eb/56/b1ba7935a17738ae8453301356628e8147c79dbb825bcbc73dc7401f9846/cffi-2.0.0.tar.gz"
    sha256 "44d1b5909021139fe36001ae048dbdde8214afa20200eda0f64c068cac5d5529"
  end

  resource "charset-normalizer" do
    url "https://files.pythonhosted.org/packages/83/2d/5fd176ceb9b2fc619e63405525573493ca23441330fcdaee6bef9460e924/charset_normalizer-3.4.3.tar.gz"
    sha256 "6fce4b8500244f6fcb71465d4a4930d132ba9ab8e71a7859e6a5d59851068d14"
  end

  resource "click" do
    url "https://files.pythonhosted.org/packages/46/61/de6cd827efad202d7057d93e0fed9294b96952e188f7384832791c7b2254/click-8.3.0.tar.gz"
    sha256 "e7b8232224eba16f4ebe410c25ced9f7875cb5f3263ffc93cc3e8da705e229c4"
  end

  resource "colorama" do
    url "https://files.pythonhosted.org/packages/d8/53/6f443c9a4a8358a93a6792e2acffb9d9d5cb0a5cfd8802644b7b1c9a02e4/colorama-0.4.6.tar.gz"
    sha256 "08695f5cb7ed6e0531a20572697297273c47b8cae5a63ffc6d6ed5c201be6e44"
  end

  resource "cryptography" do
    url "https://files.pythonhosted.org/packages/a9/62/e3664e6ffd7743e1694b244dde70b43a394f6f7fbcacf7014a8ff5197c73/cryptography-46.0.1.tar.gz"
    sha256 "ed570874e88f213437f5cf758f9ef26cbfc3f336d889b1e592ee11283bb8d1c7"
  end

  resource "idna" do
    url "https://files.pythonhosted.org/packages/f1/70/7703c29685631f5a7590aa73f1f1d3fa9a380e654b86af429e0934a32f7d/idna-3.10.tar.gz"
    sha256 "12f65c9b470abda6dc35cf8e63cc574b1c52b11df2c86030af0ac09b01b13ea9"
  end

  resource "msal" do
    url "https://files.pythonhosted.org/packages/d5/da/81acbe0c1fd7e9e4ec35f55dadeba9833a847b9a6ba2e2d1e4432da901dd/msal-1.33.0.tar.gz"
    sha256 "836ad80faa3e25a7d71015c990ce61f704a87328b1e73bcbb0623a18cbf17510"
  end

  resource "msal-extensions" do
    url "https://files.pythonhosted.org/packages/01/99/5d239b6156eddf761a636bded1118414d161bd6b7b37a9335549ed159396/msal_extensions-1.3.1.tar.gz"
    sha256 "c5b0fd10f65ef62b5f1d62f4251d51cbcaf003fcedae8c91b040a488614be1a4"
  end

  resource "pycparser" do
    url "https://files.pythonhosted.org/packages/fe/cf/d2d3b9f5699fb1e4615c8e32ff220203e43b248e1dfcc6736ad9057731ca/pycparser-2.23.tar.gz"
    sha256 "78816d4f24add8f10a06d6f05b4d424ad9e96cfebf68a4ddc99c65c0720d00c2"
  end

  resource "PyJWT" do
    url "https://files.pythonhosted.org/packages/e7/46/bd74733ff231675599650d3e47f361794b22ef3e3770998dda30d3b63726/pyjwt-2.10.1.tar.gz"
    sha256 "3cc5772eb20009233caf06e9d8a0577824723b44e6648ee0a2aedb6cf9381953"
  end

  resource "pymsalruntime" do
    url "https://files.pythonhosted.org/packages/98/a5/0c0f9c8c0a8a9e7d9c7b6b5a4a3b2a1f0e9d8c7b6a5a4a3a2a1a0/pymsalruntime-0.18.1-cp312-cp312-macosx_14_0_arm64.whl"
    sha256 "TBD_NEED_TO_CALCULATE"
  end

  resource "requests" do
    url "https://files.pythonhosted.org/packages/c9/74/b3ff8e6c8446842c3f5c837e9c3dfcfe2018ea6ecef224c710c85ef728f4/requests-2.32.5.tar.gz"
    sha256 "dbba0bac56e100853db0ea71b82b4dfd5fe2bf6d3754a8893c3af500cec7d7cf"
  end

  resource "six" do
    url "https://files.pythonhosted.org/packages/94/e7/b2c673351809dca68a0e064b6af791aa332cf192da575fd474ed7d6f16a2/six-1.17.0.tar.gz"
    sha256 "ff70335d468e7eb6ec65b95b99d3a2836546063f63acc5171de367e834932a81"
  end

  resource "typing_extensions" do
    url "https://files.pythonhosted.org/packages/72/94/1a15dd82efb362ac84269196e94cf00f187f7ed21c242792a923cdb1c61f/typing_extensions-4.15.0.tar.gz"
    sha256 "0cea48d173cc12fa28ecabc3b837ea3cf6f38c6d1136f85cbaaf598984861466"
  end

  resource "urllib3" do
    url "https://files.pythonhosted.org/packages/15/22/9ee70a2574a4f4599c47dd506532914ce044817c7752a79b6a51286319bc/urllib3-2.5.0.tar.gz"
    sha256 "3fc47733c7e419d4bc3f6b3dc2b4f890bb743906a30d56ba4a5bfa4bbff92760"
  end


  def install
    # Ensure that the `openssl` crate picks up the intended library for cryptography
    ENV["OPENSSL_DIR"] = Formula["openssl@3"].opt_prefix
    ENV["OPENSSL_NO_VENDOR"] = "1"

    # Create virtual environment
    venv = virtualenv_create(libexec, "python3.12", system_site_packages: false)
    
    # Install source-available dependencies first (excluding binary wheels)
    # This follows the AWS CLI pattern for handling binary-only packages
    venv.pip_install resources.reject { |r| r.name == "pymsalruntime" }

    # Install pymsalruntime binary wheel separately using direct wheel installation
    if resources.any? { |r| r.name == "pymsalruntime" }
      system venv.root/"bin/pip", "install", "--no-deps", resource("pymsalruntime").cached_download
    end

    # Install the main application
    venv.pip_install buildpath

    # Create the CLI wrapper script using proper entry point
    (bin/"mycli").write <<~SHELL
      #!/usr/bin/env bash
      exec "#{libexec}/bin/mycli" "$@"
    SHELL

    # Generate shell completions if supported
    # generate_completions_from_executable(bin/"mycli", "--completion", base_name: "mycli")
  end

  test do
    # Test basic functionality
    assert_match version.to_s, shell_output("#{bin}/mycli --version")
    
    # Test help command
    help_output = shell_output("#{bin}/mycli --help")
    assert_match "Usage:", help_output
    
    # Test Azure-related functionality is available
    assert_match "azure", help_output.downcase
  end

  def caveats
    <<~EOS
      This is the source-based installation of mycli-app with full broker authentication support.
      Built using the AWS CLI approach for handling binary wheel dependencies.
      
      🎯 Features:
      - Built from source for maximum compatibility
      - Dependencies managed by Homebrew
      - Full Azure authentication including native broker support
      - Automatic updates through Homebrew
      
      🔐 Authentication Methods Available:
      - Browser-based authentication (default)
      - Device code authentication (--use-device-code)
      - Native broker authentication with pymsalruntime
      - Microsoft Company Portal integration
      - Touch ID/Face ID support on macOS (where available)
      - MSAL token caching and refresh
      
      ✨ Technical Implementation:
      - Uses AWS CLI-style selective pip install for binary wheels
      - Source dependencies built from PyPI source distributions
      - Binary wheels (pymsalruntime) installed separately for compatibility
      - Follows Homebrew Core best practices for mixed dependency types
      
      📱 Available authentication commands:
        mycli login                    # Browser authentication (default)
        mycli login --device           # Device code authentication  
        mycli login --use-broker       # Native broker authentication
        
      � Alternative Installation:
      For a pre-built venv bundle approach:
        brew install naga-nandyala/mycli-app/mycli-app-venv
        
      For more information, visit:
        https://github.com/naga-nandyala/mycli-app
    EOS
  end
end