from setuptools import setup, find_packages
import os


# Read version from the package
def get_version():
    """Get version from __init__.py"""
    version_path = os.path.join("src", "mycli_app", "__init__.py")
    with open(version_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip("\"'")
    return "1.0.0"


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mycli-app",
    version=get_version(),
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple CLI application similar to Azure CLI with Azure authentication capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/naga-nandyala/mycli-app",
    project_urls={
        "Bug Tracker": "https://github.com/naga-nandyala/mycli-app/issues",
        "Documentation": "https://github.com/naga-nandyala/mycli-app#readme",
        "Source Code": "https://github.com/naga-nandyala/mycli-app",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Environment :: Console",
        "Typing :: Typed",
    ],
    keywords="cli azure authentication command-line tool",
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "colorama>=0.4.0",
    ],
    extras_require={
        "azure": [
            "azure-identity>=1.12.0",
            "azure-mgmt-core>=1.3.0",
            "azure-core>=1.24.0",
            "msal>=1.20.0",
        ],
        "broker": [
            "azure-identity>=1.12.0",
            "azure-mgmt-core>=1.3.0",
            "azure-core>=1.24.0",
            "msal[broker]>=1.20.0,<2",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.990",
            "setuptools>=45.0.0",
            "wheel>=0.36.0",
            "twine>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mycli=mycli_app.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
