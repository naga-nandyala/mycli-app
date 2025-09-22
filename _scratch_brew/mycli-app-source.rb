# Homebrew formula for mycli-app (source-based installation)
class MycliAppSrc < Formula
  include Language::Python::Virtualenv

  desc "Simple Azure-like CLI tool by Naga (Source Installation)"
  homepage "https://github.com/naga-nandyala/mycli-app"
  url "https://github.com/naga-nandyala/mycli-app/archive/refs/tags/v1.0.1.tar.gz"
  sha256 "YOUR_SHA256_HASH_HERE"  # You'll need to update this
  license "MIT"
  head "https://github.com/naga-nandyala/mycli-app.git", branch: "main"

  livecheck do
    url :stable
    regex(/^v?(\d+(?:\.\d+)+)$/i)
    strategy :github_latest
  end

  bottle do
    # Homebrew will generate these automatically when building bottles
    # sha256 cellar: :any_skip_relocation, arm64_sequoia: "..."
    # sha256 cellar: :any_skip_relocation, arm64_sonoma:  "..."
    # etc.
  end

  depends_on "python@3.12"

  # Core dependencies
  resource "click" do
    url "https://files.pythonhosted.org/packages/96/d3/f04c7bfcf5c1862a2a5b845c6b2b360488cf47af55dfa79c98f6a6bf98b5/click-8.1.7.tar.gz"
    sha256 "ca9853ad459e787e2192211578cc907e7594e294c7ccc834310722b41b9ca6de"
  end

  resource "colorama" do
    url "https://files.pythonhosted.org/packages/d8/53/6f443c9a4a8358a93a6792e2acffb9d9d5cb0a5cfd8802644b7b1c9a02e4/colorama-0.4.6.tar.gz"
    sha256 "08695f5cb7ed6e0531a20572697297273c47b8cae5a63ffc6d6ed5c201be6e44"
  end

  # Azure dependencies (optional but included for full functionality)
  resource "azure-identity" do
    url "https://files.pythonhosted.org/packages/73/4b/6c5f5faa71fad9db7e05b3ad7f6e85a57ab15e0137c65b7baaf00b3e7e82/azure-identity-1.17.1.tar.gz"
    sha256 "a14b1f01c7036f11f148f22cd8c16e05ac75ac45d9f0a4c4b801793a0e72f058"
  end

  resource "azure-core" do
    url "https://files.pythonhosted.org/packages/ce/89/f53968635b1b2e53e4aad2dd641488929fef4ca9dfb0b97927fa7697ddf3/azure_core-1.35.0.tar.gz"
    sha256 "c0be528489485e9ede59b6971eb63c1eaacf83ef53001bfe3904e475e972be5c"
  end

  resource "azure-mgmt-core" do
    url "https://files.pythonhosted.org/packages/14/95/2b2085e40f4b9de88ad256428a669583066d8ab348fc19110c7d04c3189b/azure-mgmt-core-1.4.0.zip"
    sha256 "d195208340094f98e5a6661b781cde6f6a051e79ce317caabd8ff97030a9b3ae"
  end

  resource "msal" do
    url "https://files.pythonhosted.org/packages/59/04/8d7734643abd6bc1694a8a23c5b3f52edf5b9b2be0b5ae3b4329a51a5476/msal-1.31.0.tar.gz"
    sha256 "2c4f189cf9cc8f00c80045f66d39b7c0f3ed45873fd3d1f2af9f22db2e12ff4b"
  end

  resource "requests" do
    url "https://files.pythonhosted.org/packages/63/70/2bf7780ad2d390a8d301ad0b550f1581eadbd9a20f896afe06353c2a2913/requests-2.32.3.tar.gz"
    sha256 "55365417734eb18255590a9ff9eb97e9e1da868d4ccd6402399eaf68af20a760"
  end

  resource "certifi" do
    url "https://files.pythonhosted.org/packages/b0/ee/9b19140fe824b367c04c5e1b369942dd754c4c5462d5674002f75c4dedc1/certifi-2024.8.30.tar.gz"
    sha256 "bec941d2aa8195e248a60b31ff9f0558284f70ca1ffa05fa026804e9a6a1fced"
  end

  resource "charset-normalizer" do
    url "https://files.pythonhosted.org/packages/63/09/c1bc53dab74b1816a00d8d030de5bf98f724c52c1635e07681d312f20be8/charset-normalizer-3.3.2.tar.gz"
    sha256 "f30c3cb33b24454a82faecaf01b19c18562b1e89558fb6c56de4d9118a032fd5"
  end

  resource "idna" do
    url "https://files.pythonhosted.org/packages/e8/ac/e349c5e6d4543326c6883ee9491e3921e0d07b55fdf3cce184b40d63e72a/idna-3.8.tar.gz"
    sha256 "d838c2c0ed6fced7693d5e8ab8e734d5f8fda53a039c0164afb0b82e771e3603"
  end

  resource "urllib3" do
    url "https://files.pythonhosted.org/packages/ed/63/22ba4ebfe7430b76388e7cd448d5478814d3032121827c12a2cc287e2260/urllib3-2.2.3.tar.gz"
    sha256 "e7d814a81dad81e6caf2ec9fdedb284ecc9c73076b62654547cc64ccdcae26e9"
  end

  resource "six" do
    url "https://files.pythonhosted.org/packages/71/39/171f1c67cd00715f190ba0b100d606d440a28c93c7714febeca8b79af85e/six-1.16.0.tar.gz"
    sha256 "1e61c37477a1626458e36f7b1d82aa5c9b094fa4802892072e49de9c60c4c926"
  end

  resource "cryptography" do
    url "https://files.pythonhosted.org/packages/0d/05/07b55d1fa21ac18c3a8c79f764e2514e6f6a9698f1be44994f5adf0d29db/cryptography-43.0.1.tar.gz"
    sha256 "203e92a75716d8cfb491dc47c79e17d0d9207ccffcbcb35f598fbe463ae3444d"
  end

  # Build dependencies for cryptography
  depends_on "rust" => :build
  depends_on "pkgconf" => :build
  depends_on "openssl@3"

  uses_from_macos "libffi"

  def install
    # Ensure that the `openssl` crate picks up the intended library for cryptography
    ENV["OPENSSL_DIR"] = Formula["openssl@3"].opt_prefix
    ENV["OPENSSL_NO_VENDOR"] = "1"

    # Create virtual environment
    venv = virtualenv_create(libexec, "python3.12", system_site_packages: false)
    
    # Install all Python dependencies
    venv.pip_install resources

    # Install the main application
    venv.pip_install buildpath

    # Create the CLI wrapper script
    (bin/"mycli").write <<~SHELL
      #!/usr/bin/env bash
      PYTHONPATH="#{libexec}/lib/python3.12/site-packages" #{libexec}/bin/python -m mycli_app.cli "$@"
    SHELL

    # Generate shell completions if click supports it
    # generate_completions_from_executable(bin/"mycli", "--completion", base_name: "mycli")
  end

  test do
    # Test basic functionality
    assert_match "MyCliApp version", shell_output("#{bin}/mycli --version")
    
    # Test help command
    help_output = shell_output("#{bin}/mycli --help")
    assert_match "Usage:", help_output
    
    # Test Azure-related functionality is available
    assert_match "azure", help_output.downcase
  end

  def caveats
    <<~EOS
      This is the source-based installation of mycli-app, which builds from source
      and manages dependencies through Homebrew's Python virtual environment system.
      
      Features:
      - Built from source for maximum compatibility
      - Dependencies managed by Homebrew
      - Azure authentication with MSAL support
      - Automatic updates through Homebrew
      
      Benefits of this approach:
      - Smaller download size
      - Better integration with system Python
      - Easier dependency management
      - Automatic security updates for dependencies
      
      To use Azure authentication features, run:
        mycli --help
        
      For the alternative venv bundle version, install:
        brew install naga-nandyala/mycli-app/mycli-app-venv
        
      For more information, visit:
        https://github.com/naga-nandyala/mycli-app
    EOS
  end
end