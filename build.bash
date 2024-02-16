#!/bin/bash
set -euo pipefail

pip install -r tools/requirements.txt
python tools/update-mono-list.py
mkdir -p built
python tools/build.py filters/main.yml --hosts built/hosts.txt --abp built/abp.txt --domains built/domains.txt
