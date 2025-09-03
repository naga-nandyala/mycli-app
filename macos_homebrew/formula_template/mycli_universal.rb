# Homebrew formula template for a universal macOS binary of mycli
class Mycli < Formula
  desc "Simple Azure-like CLI tool"
  homepage "https://github.com/naga-nandyala/mycli-app"
  version "1.0.0" # update on release
  license "MIT"

  # Replace with the universal tarball URL & sha256 after a release
  url "https://github.com/naga-nandyala/mycli-app/releases/download/v1.0.0/mycli-1.0.0-macos-universal.tar.gz"
  sha256 "REPLACE_UNIVERSAL_SHA256"

  def install
    bin.install "mycli"
  end

  test do
    assert_match "MyCliApp version", shell_output("#{bin}/mycli --version")
  end
end
