#!/bin/sh
set -e
set -x

# lint first
bash ./scripts/lint.sh

# run tests
pytest
