#!/bin/bash
# Navigate to the parent directory to access setup.py
cd "$(dirname "$0")/.." || exit
# Build the package
python setup.py sdist bdist_wheel
