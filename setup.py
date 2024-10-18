from setuptools import setup, find_packages
import subprocess
import os


def list_dist(version):
    """List the distribution files in the 'dist' directory."""
    try:
        import glob
        files = glob.glob(f"dist/airtable_sync-{version}*")
        if not files:
            print(
                f"No files found for version {version} in the 'dist' directory.")
        else:
            print("Files created:")
            subprocess.run(["ls"] + files, check=True)
    except Exception as e:
        print(f"Error listing dist: {e}")
        exit(1)


def get_version():
    """Get the latest version tag from the git repository."""
    try:
        # Get the latest tag
        version = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"]
        ).strip().decode('utf-8')

        # Remove the 'v' prefix if present
        if version.startswith("v"):
            version = version[1:]

        return version
    except Exception as e:
        print(f"Error getting version: {e}")
        return "0.0.0"  # Default version if something goes wrong


def create_tag(tag):
    """Create a git tag and push it to the remote repository."""
    print(f"Creating tag '{tag}' ...")

    try:
        subprocess.run(["git", "tag", tag], check=True)
        subprocess.run(["git", "push", "origin", tag], check=True)
        print(f"Tag '{tag}' created and pushed.")
    except Exception as e:
        print(f"Error creating tag: {e}")
        exit(1)


def confirm_version(version):
    """Present version options to the user and return the chosen version."""
    print(f"Detected version: v{version}. Choose an option:")

    # Show options
    print("1. Use latest v" + version)
    print("2. Create v" +
          increment_version(version, patch=True, preview=True))
    print("3. Create v" +
          increment_version(version, minor=True, preview=True))
    print("4. Create v" +
          increment_version(version, major=True, preview=True))
    print("5. Exit")

    choice = input("Enter your choice (1/2/3/4/5): ")
    if choice == '1':
        return version  # Keep current version
    elif choice == '2':
        new_version = increment_version(version, patch=True)
        create_tag(f"v{new_version}")  # Create new tag
        return new_version
    elif choice == '3':
        new_version = increment_version(version, minor=True)
        create_tag(f"v{new_version}")  # Create new tag
        return new_version
    elif choice == '4':
        new_version = increment_version(version, major=True)
        create_tag(f"v{new_version}")  # Create new tag
        return new_version
    else:
        exit(0)


def confirm_build_with_version(version):
    """Confirm the build with the specified version."""
    print(f"Building with version: v{version}.")
    choice = input("Continue building? (y/n): ")
    if choice.lower() != 'y':
        exit(0)
    return version


def increment_version(version, patch=False, minor=False, major=False, preview=False):
    """Increment the version number based on the specified type (patch, minor, major)."""
    major_num, minor_num, patch_num = map(int, version.split('.'))

    if major:
        major_num += 1
        minor_num = 0
        patch_num = 0
    elif minor:
        minor_num += 1
        patch_num = 0
    elif patch:
        patch_num += 1

    new_version = f"{major_num}.{minor_num}.{patch_num}"
    return new_version  # Return new version regardless of preview flag


# Read the contents of your README file for the long description
with open("README.md", "r") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r") as fh:
    requirements = fh.read().splitlines()

version = get_version()  # Get the version
version = confirm_version(version)  # Confirm the version

confirm_build_with_version(version)

setup(
    name="airtable_sync",
    version=version,  # Use the confirmed version
    author="Zhongkai Ren",
    author_email="zhongkai.ren@unity3d.com",
    description="A Python package to synchronize GitHub issues with Airtable.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zhongkairen/airtable-sync",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    include_package_data=True,
    exclude_package_data={
        'airtable_sync': ['config.json'],
    },
    entry_points={
        'console_scripts': [
            'airtable-sync=airtable_sync.main:main',
        ],
    },
)

list_dist(version)
