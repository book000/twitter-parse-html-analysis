#!/usr/bin/env python3
"""
Setup script for Twitter HTML Parser & Analysis Tool
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = (
    readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
)

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = [
            line.strip() for line in f if line.strip() and not line.startswith("#")
        ]
else:
    requirements = ["beautifulsoup4>=4.12.0", "lxml>=4.9.0"]

setup(
    name="twitter-parse-html-analysis",
    version="1.0.0",
    description="Comprehensive Twitter export data parser with advanced analysis capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Twitter HTML Parser Project",
    author_email="https://github.com/yourusername/twitter-parse-html-analysis",
    url="https://github.com/yourusername/twitter-parse-html-analysis",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/twitter-parse-html-analysis/issues",
        "Source": "https://github.com/yourusername/twitter-parse-html-analysis",
        "Documentation": "https://github.com/yourusername/twitter-parse-html-analysis#readme",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "analysis": [
            "pandas>=2.0.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "scikit-learn>=1.3.0",
        ],
        "cli": [
            "click>=8.1.0",
            "tqdm>=4.65.0",
        ],
        "full": [
            "pandas>=2.0.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "scikit-learn>=1.3.0",
            "click>=8.1.0",
            "tqdm>=4.65.0",
            "nltk>=3.8",
            "textblob>=0.17.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "twitter-parse=scripts.extract_tweets:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    keywords=[
        "twitter",
        "parsing",
        "html",
        "analysis",
        "social-media",
        "data-extraction",
        "nlp",
        "text-analysis",
        "video-misuse-detection",
    ],
    include_package_data=True,
    zip_safe=False,
)
