#!/bin/sh
set -e
set -x

# put every import on one line for autoflake remove unused imports
isort baguette tests examples --force-single-line-imports
# remove unused imports and variables
autoflake baguette tests examples --remove-all-unused-imports --recursive --remove-unused-variables --in-place --exclude=__init__.py

# format code
black baguette tests examples --line-length 80

# resort imports
isort baguette tests examples
