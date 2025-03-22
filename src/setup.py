from setuptools import setup, find_packages

setup(
    name="lef",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "boto3>=1.26.0",
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "python-dotenv>=0.19.0",
        "requests>=2.28.0"
    ],
    python_requires=">=3.8",
) 