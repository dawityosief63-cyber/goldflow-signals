from setuptools import setup, find_packages

setup(
    name="goldflow-signals",
    version="0.1.0",
    description="Open-source footprint-chart signal library",
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.8",
    license="MIT",
)
