#!/bin/bash
set -euo pipefail

DAY_RANGE=2 ./nrd-list-downloader/nrd-list-downloader.sh
pip install aiohttp[speedups]
pip install -r tools/requirements.txt
python tools/update-fedex-list.py
python tools/update-mono-list.py
python tools/update-prizes-list.py

if git diff-index --quiet HEAD; then
	echo "Nothing to do!"
else
	mkdir -p built
	python tools/build.py filters/main.yml --hosts built/hosts.txt --abp built/abp.txt --domains built/domains.txt
fi
