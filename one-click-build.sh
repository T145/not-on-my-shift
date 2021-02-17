#!/bin/bash

set -euo pipefail
cd $(dirname "$0")

# Create environment if it does not exist
if [ ! -d venv ]; then
	virtualenv -p python3 venv

	# Activate it
	source venv/bin/activate
else
	# If it exists, just activate it
	source venv/bin/activate
fi

# Install requirements
pip install -r tools/requirements.txt

# Create build directory
[ -d built ] || mkdir built

# Finally build it
python tools/build.py filters/main.yml --hosts built/hosts.txt --domains built/domains.txt --abp built/abp.txt
