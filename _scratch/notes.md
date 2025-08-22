Cross-Compilation Limitations: macOS .pkg installers typically need to be built on a Mac system because they require macOS-specific tools, frameworks, and signing capabilities. Creating a truly native .pkg package fully compatible with macOS on a non-Mac system is difficult.

Use Python Packaging Tools Like py2app: The common way to package Python scripts into macOS standalone apps is with tools like py2app, which bundles your Python code into a Mac app bundle (.app). However, to create a .pkg installer from this .app, you typically do this through macOS packaging tools.

Virtual Mac Environments or CI Services: One popular workaround is to use a cloud macOS environment or continuous integration services (e.g., GitHub Actions with macOS runners, MacStadium) that provide remote Mac access to run macOS packaging tools and generate .pkg files for you.

Manual .pkg Creation on Mac: If you can access a Mac temporarily (e.g., friends, rental, or virtual), you can create a .pkg by first bundling your Python app using py2app or PyInstaller for macOS, then package it using the productbuild or pkgbuild command-line tools native to macOS.

Python's distutils and setup.py: Python's distutils can create Python packages but does not inherently create macOS .pkg installers. It handles Python module packaging more than full app installers.