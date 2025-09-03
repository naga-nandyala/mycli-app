# Homebrew formula template selecting binary per architecture
class Mycli < Formula
  desc "Simple Azure-like CLI tool"
  homepage "https://github.com/naga-nandyala/mycli-app"
  version "1.0.0" # update on release
  license "MIT"

  if Hardware::CPU.arm?
    url "https://github.com/naga-nandyala/mycli-app/releases/download/v1.0.0/mycli-1.0.0-macos-arm64.tar.gz"
    sha256 "REPLACE_ARM64_SHA256"
  else
    url "https://github.com/naga-nandyala/mycli-app/releases/download/v1.0.0/mycli-1.0.0-macos-x86_64.tar.gz"
    sha256 "REPLACE_X86_64_SHA256"
  end

  def install
    bin.install "mycli"
  end

  test do
    assert_match "MyCliApp version", shell_output("#{bin}/mycli --version")
  end
end
