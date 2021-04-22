#!/bin/sh
set -e
set -x

# lint first
bash ./scripts/lint.sh

# run tests with coverager info
pytest --cov=baguette --cov-report=term-missing --cov-report=xml tests
