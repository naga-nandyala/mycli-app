#!/usr/bin/env python3
"""
Script to update Homebrew formula with latest release information from GitHub.
This script fetches the latest release info and updates the formula template.
"""

import re
import requests
import sys
from pathlib import Path


def get_latest_release_info(repo_owner, repo_name):
    """Fetch latest release information from GitHub API."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"

    try:
        response = requests.get(url)
        response.raise_for_status()
        release_data = response.json()

        version = release_data["tag_name"].lstrip("v")  # Remove 'v' prefix if present
        assets = release_data["assets"]

        # Find the asset files we need
        arm64_asset = None
        x86_64_asset = None

        for asset in assets:
            if "macos-arm64.tar.gz" in asset["name"] and not asset["name"].endswith(".sha256"):
                arm64_asset = asset
            elif "macos-x86_64.tar.gz" in asset["name"] and not asset["name"].endswith(".sha256"):
                x86_64_asset = asset

        if not arm64_asset or not x86_64_asset:
            print("Error: Could not find required ARM64 or x86_64 assets")
            return None

        return {
            "version": version,
            "arm64_url": arm64_asset["browser_download_url"],
            "x86_64_url": x86_64_asset["browser_download_url"],
        }

    except requests.RequestException as e:
        print(f"Error fetching release info: {e}")
        return None


def get_sha256_from_github(asset_url):
    """Download and get SHA256 from the .sha256 file on GitHub."""
    sha256_url = asset_url + ".sha256"

    try:
        response = requests.get(sha256_url)
        response.raise_for_status()
        # The .sha256 file typically contains just the hash
        return response.text.strip().split()[0]
    except requests.RequestException as e:
        print(f"Error fetching SHA256 for {asset_url}: {e}")
        return None


def update_formula_template(template_path, release_info):
    """Update the Homebrew formula template with new release information."""

    # Get SHA256 hashes
    arm64_sha256 = get_sha256_from_github(release_info["arm64_url"])
    x86_64_sha256 = get_sha256_from_github(release_info["x86_64_url"])

    if not arm64_sha256 or not x86_64_sha256:
        print("Error: Could not fetch SHA256 hashes")
        return False

    try:
        with open(template_path, "r") as f:
            content = f.read()

        # Update version
        content = re.sub(r'version\s+"[^"]*"', f'version "{release_info["version"]}"', content)

        # Update ARM64 SHA256
        content = re.sub(
            r'(if Hardware::CPU\.arm\?\s*\n\s*url.*\n\s*sha256\s+")[^"]*(")',
            rf"\g<1>{arm64_sha256}\g<2>",
            content,
            flags=re.MULTILINE | re.DOTALL,
        )

        # Update x86_64 SHA256
        content = re.sub(
            r'(else\s*\n\s*url.*\n\s*sha256\s+")[^"]*(")',
            rf"\g<1>{x86_64_sha256}\g<2>",
            content,
            flags=re.MULTILINE | re.DOTALL,
        )

        with open(template_path, "w") as f:
            f.write(content)

        print(f"✅ Updated formula template with version {release_info['version']}")
        print(f"   ARM64 SHA256: {arm64_sha256}")
        print(f"   x86_64 SHA256: {x86_64_sha256}")
        return True

    except Exception as e:
        print(f"Error updating formula template: {e}")
        return False


def main():
    """Main function to update Homebrew formula."""
    repo_owner = "naga-nandyala"
    repo_name = "mycli-app"

    # Get the formula path (now in the main repo)
    script_dir = Path(__file__).parent.parent  # Go up to main repo root
    template_path = script_dir / "Formula" / "mycli.rb"

    if not template_path.exists():
        print(f"Error: Formula not found at {template_path}")
        sys.exit(1)

    print(f"Fetching latest release info for {repo_owner}/{repo_name}...")
    release_info = get_latest_release_info(repo_owner, repo_name)

    if not release_info:
        print("Failed to fetch release information")
        sys.exit(1)

    print(f"Found latest release: v{release_info['version']}")

    if update_formula_template(template_path, release_info):
        print("✅ Formula template updated successfully!")
    else:
        print("❌ Failed to update formula template")
        sys.exit(1)


if __name__ == "__main__":
    main()
