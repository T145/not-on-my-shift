#!/bin/bash

set -euo pipefail
cd $(dirname "$0")

# Create environment if it does not exist
if [ ! -d venv ]; then
	virtualenv -p python3 venv

	# Activate it
	source venv/bin/activate

	# Install requirements
	pip install -r requirements.txt
else
	# If it exists, just activate it
	source venv/bin/activate
fi

# Create build directory
[ -d built ] || mkdir built

# Finally build it
python build.py filters.yml --hosts built/hosts.txt --domains built/domains.txt --abp built/abp.txt
