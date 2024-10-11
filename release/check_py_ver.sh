#!/bin/bash
# Check the Python version compatibility of the package

# List of required Python versions
required_versions=("3.6.15" "3.7.16" "3.8.16" "3.9.16" "3.10.15" "3.11.5")

# Function to check if a Python version is installed via pyenv
check_and_install_python() {
    version=$1
    if pyenv versions --bare | grep -q "^$version\$"; then
        echo "Python $version is already installed."
    else
        echo "Installing Python $version..."
        pyenv install $version
    fi
}

# Function to ensure tox is installed in each Python version
ensure_tox_installed() {
    version=$1
    pyenv shell $version
    if ! pip show tox > /dev/null 2>&1; then
        echo "Installing tox for Python $version..."
        pip install tox
    else
        echo "tox is already installed for Python $version."
    fi
}

# Install any missing Python versions
for version in "${required_versions[@]}"; do
    check_and_install_python $version
    ensure_tox_installed $version
done

# Build the wheel package
echo "Building the package as a wheel..."
python setup.py bdist_wheel

# Create a tox.ini file
cat <<EOL > tox.ini
[tox]
envlist = py38, py39, py310, py311

[testenv]
commands = python -m airtable_sync
install_command = pip install --prefer-binary {opts} {packages}
EOL

# Run tox
echo "Running tests with tox..."
tox

# Remove tox.ini after running tests
rm tox.ini
echo "Removed tox.ini."
