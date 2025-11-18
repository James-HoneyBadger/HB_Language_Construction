#!/usr/bin/env python3
"""
Setup script for Honey Badger Language Construction Set
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8")

setup(
    name="hb-lcs",
    version="1.0.0",
    author="Honey Badger",
    description="Honey Badger Language Construction Set - Create custom programming language variants",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/James-HoneyBadger/Language_Construction_Set",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Interpreters",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    license="MIT",
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
        "ide": [
            "tkinter",  # Usually comes with Python, but listed for completeness
        ],
    },
    entry_points={
        "console_scripts": [
            "hblcs=hb_lcs.cli:main",
            "hblcs-ide=hb_lcs.launch_ide:main",
        ],
    },
    include_package_data=True,
    package_data={
        "hb_lcs": ["*.json", "*.yaml"],
    },
)
