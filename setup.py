from setuptools import setup, find_packages
setup(
    name="quilt-multi-oracle",
    version="0.1.0",
    description="Multi-model JEV oracle — probes canon lores across N LLM workers in parallel",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Casey / SuperInstance",
    packages=find_packages(exclude=["tests", "demos"]),
    python_requires=">=3.8",
    install_requires=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
