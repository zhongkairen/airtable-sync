from setuptools import setup, find_packages

# Read the contents of your README file for the long description
with open("README.md", "r") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r") as fh:
    requirements = fh.read().splitlines()

setup(
    name="airtable_sync",
    version="0.1.6",
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
    python_requires='>=3.6',
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
