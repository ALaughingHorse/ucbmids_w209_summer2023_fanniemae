from setuptools import find_packages, setup
import os
name = os.path.split(os.getcwd())[1]
setup(
    name=name,
    packages=find_packages(),
    package_dir={"":"src"},
    version="0.1.0",
    description="W203 Mids Projects",
    author="Xiao Ma",
    license="MIT"
)