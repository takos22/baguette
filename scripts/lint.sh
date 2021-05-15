#!/bin/sh
set -e
set -x

# lint code
./scripts/lint-code.sh

# lint docs and README
./scripts/lint-docs.sh
