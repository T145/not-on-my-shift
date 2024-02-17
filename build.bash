#!/bin/bash
set -euo pipefail

DAY_RANGE=1 ./nrd-list-downloader/nrd-list-downloader.sh
pip install -r tools/requirements.txt
#python tools/update-fedex-list.py
python tools/update-mono-list.py
python tools/update-prizes-list.py
mkdir -p built
python tools/build.py filters/main.yml --hosts built/hosts.txt --abp built/abp.txt --domains built/domains.txt
