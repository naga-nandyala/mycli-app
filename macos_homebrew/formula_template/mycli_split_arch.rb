# Homebrew formula template selecting binary per architecture
class Mycli < Formula
  desc "Simple Azure-like CLI tool"
  homepage "https://github.com/naga-nandyala/mycli-app"
  version "0.1.0" # TODO: Update this version and SHA256s for each release
  license "MIT"

  base_url = "https://github.com/naga-nandyala/mycli-app/releases/download/v#{version}"
  
  if Hardware::CPU.arm?
    url "#{base_url}/mycli-#{version}-macos-arm64.tar.gz"
    sha256 "e283f201e6f05659369434376973a76891d542da356a9b191d1b786b3188eae3" # Update for each release
  else
    url "#{base_url}/mycli-#{version}-macos-x86_64.tar.gz"
    sha256 "8d74eec878a5f241d7f1f3f6585c68d25ddda784ebe19a97b9607c2ab6d0b64c" # Update for each release
  end

  def install
    bin.install "mycli"
  end

  test do
    assert_match "MyCliApp version", shell_output("#{bin}/mycli --version")
  end
end
