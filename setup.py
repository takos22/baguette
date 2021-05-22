import os
import re

from setuptools import setup


def get_version(package):
    """Return package version as listed in `__version__` in `init.py`."""

    path = os.path.join(package, "__init__.py")
    version = ""
    with open(path, "r", encoding="utf8") as init_py:
        version = re.search(
            r"^__version__\s*=\s*['\"]([^'\"]*)['\"]",
            init_py.read(),
            re.MULTILINE,
        ).group(1)

    if not version:
        raise RuntimeError(f"__version__ is not set in {path}")

    return version


def get_packages(package):
    """Return root package and all sub-packages."""

    return [
        dirpath
        for dirpath, *_ in os.walk(package)
        if os.path.exists(os.path.join(dirpath, "__init__.py"))
    ]


def get_long_description(filename: str = "README.rst"):
    """Return the README."""

    with open(filename, "r", encoding="utf8") as readme:
        long_description = readme.read()
    return long_description


def get_requirements(filename: str = "requirements.txt"):
    """Return the requirements."""

    requirements = []
    with open(filename, "r", encoding="utf8") as requirements_txt:
        requirements = requirements_txt.read().splitlines()
    return requirements


extra_requires = {
    "uvicorn": ["uvicorn[standard]"],
}

setup(
    name="baguette",
    version=get_version("baguette"),
    url="https://github.com/takos22/baguette",
    license="MIT",
    description="Asynchronous web framework.",
    long_description=get_long_description(),
    long_description_content_type="text/x-rst",
    author="takos22",
    author_email="takos2210@gmail.com",
    packages=get_packages("baguette"),
    python_requires=">=3.6",
    install_requires=get_requirements(),
    extras_require=extra_requires,
    project_urls={
        "Documentation": "https://baguette.readthedocs.io/",
        "Issue tracker": "https://github.com/takos22/baguette/issues",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
