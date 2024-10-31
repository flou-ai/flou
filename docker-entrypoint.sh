#!/bin/bash

# exit if there's an error
set -e

# install local flou
pip install -e /code/flou

# install local project requirements
if [ -f /code/app/requirements.txt ]; then
    echo "Project's requirements.txt found. Installing..."
    pip install -r /code/app/requirements.txt
else
    echo "No project's requirements.txt found. Skipping..."
fi

exec "$@"