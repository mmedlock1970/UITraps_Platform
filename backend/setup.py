from setuptools import setup, find_packages

setup(
    name="ui_traps_analyzer",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "anthropic>=0.40.0",
        "python-dotenv>=1.0.0",
    ],
)