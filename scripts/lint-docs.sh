#!/bin/sh
set -e
set -x

folders="docs"

# check the docs with doc8
doc8 $folders --quiet

# check package build for README.rst
python3 setup.py --quiet sdist
twine check dist/*
