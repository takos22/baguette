#!/bin/sh
set -e

lint=true

# no linitng if -n or --no-lint flag
for arg in "$@"
do
    if [ "$arg" == "-n" ] || [ "$arg" == "--no-lint" ]; then
        lint=false
    fi
done

if [ "$lint" = true ]; then
    set -x
    # lint
    ./scripts/lint.sh
else
    set -x
fi

# run tests
pytest
