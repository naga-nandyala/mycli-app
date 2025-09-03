class Mycli < Formula
  desc "CLI tool similar to Azure CLI for cloud management"
  homepage "https://github.com/naga-nandyala/mycli-app"
  version "__VERSION__"
  license "MIT"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/naga-nandyala/mycli-app/releases/download/v__VERSION__/mycli-__VERSION__-macos-arm64.zip"
      sha256 "__ARM_SHA__"
    else
      url "https://github.com/naga-nandyala/mycli-app/releases/download/v__VERSION__/mycli-__VERSION__-macos-x64.zip"
      sha256 "__X64_SHA__"
    end
  end

  def install
    bin.install "mycli"
  end

  test do
    assert_match "MyCliApp version", shell_output("#{bin}/mycli --version")
  end
end
