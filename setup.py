"""
--------------------------------------------------------------------------------
AUTHOR:      Nishar A Sunkesala / FixMyK8s
PURPOSE:     Installation script for KubeCuro (Bridge for pyproject.toml).
LICENSE:     Apache License 2.0
--------------------------------------------------------------------------------
"""
import os
from setuptools import setup, find_packages

# Load the README for the long description on PyPI/distribution
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="kubecuro",
    version="1.0.0",
    author="Nishar A Sunkesala",
    author_email="fixmyk8s@protonmail.com", 
    description="Kubernetes Logic Diagnostics & YAML Auto-Healer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fixmyk8s/kubecuro", # Replace with your actual URL
    
    # Root of the package source
    package_dir={"": "src"}, 
    packages=find_packages(where="src"),
    
    # Dependencies aligned with production scripts
    install_requires=[
        "ruamel.yaml>=0.17.0",
        "rich>=12.0.0",
    ],
    
    # CLI entry point logic
    entry_points={
        "console_scripts": [
            "kubecuro=kubecuro.main:run", 
        ],
    },
    
    # Metadata and Compliance
    include_package_data=True,
    python_requires=">=3.7",
    license="Apache-2.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Diagnostics",
    ],
)
