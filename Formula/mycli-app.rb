# Homebrew formula for mycli-app
class MycliApp < Formula
  desc "Simple Azure-like CLI tool by Naga"
  homepage "https://github.com/naga-nandyala/mycli-app"
  version "0.1.2"
  license "MIT"

  base_url = "https://github.com/naga-nandyala/mycli-app/releases/download/v#{version}"
  
  if Hardware::CPU.arm?
    url "#{base_url}/mycli-#{version}-macos-arm64.tar.gz"
    sha256 "557f6b4383fc55548af30de7d6378c26d8d9cf00c05f8be4e8bd28085ea3f836"
  else
    url "#{base_url}/mycli-#{version}-macos-x86_64.tar.gz"
    sha256 "b1c38c5dcdd8902bbaab2afa462195bdd2a7b47018972b244d96fcd8769e17f1"
  end

  def install
    bin.install "mycli"
  end

  test do
    assert_match "MyCliApp version", shell_output("#{bin}/mycli --version")
  end
end
