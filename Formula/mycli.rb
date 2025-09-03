# Homebrew formula for mycli
class Mycli < Formula
  desc "Simple Azure-like CLI tool"
  homepage "https://github.com/naga-nandyala/mycli-app"
  version "0.1.0"
  license "MIT"

  base_url = "https://github.com/naga-nandyala/mycli-app/releases/download/v#{version}"
  
  if Hardware::CPU.arm?
    url "#{base_url}/mycli-#{version}-macos-arm64.tar.gz"
    sha256 "0cb05d9e0c95a284542753f02dea0887dce480803022b6e45695029335350db8"
  else
    url "#{base_url}/mycli-#{version}-macos-x86_64.tar.gz"
    sha256 "8d74eec878a5f241d7f1f3f6585c68d25ddda784ebe19a97b9607c2ab6d0b64c"
  end

  def install
    bin.install "mycli"
  end

  test do
    assert_match "MyCliApp version", shell_output("#{bin}/mycli --version")
  end
end
