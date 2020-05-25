#!/bin/bash -e

set -e
set -o pipefail

cd "$(dirname "$0")"

git add filters.yml
if git diff-index --cached --quiet HEAD; then
	echo "Nothing to do"
else
	git commit -m "Updated filters"
	git push
fi
