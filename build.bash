#!/bin/bash

set -euo pipefail

# Install requirements
pip install -r tools/requirements.txt

# Create build directory
mkdir -p built

# Finally build it
python tools/build.py filters/main.yml --hosts built/hosts.txt --abp built/abp.txt --domains built/domains.txt
