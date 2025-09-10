from setuptools import setup, find_packages

setup(
    name="clq",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.5.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "clq=clq.cli:main",
        ],
    },
    author="CLQ Team",
    description="UEFA Champions League Qualifying statistics and quiz generator",
    python_requires=">=3.8",
)