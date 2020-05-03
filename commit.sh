#!/bin/bash -e

set -e
set -o pipefail

cd "$(dirname "$0")"

changed=$(git status --porcelain | wc -l)
if [ $changed -eq 0 ]; then
	echo "No differences - nothing to do"
	exit 0
fi

countdiff() {
	local file="$1"
	local type="$2"

	expr \
		$(git diff          "$file" | tail -n +5 | grep ^\\${type}[^#] | wc -l) + \
		$(git diff --cached "$file" | tail -n +5 | grep ^\\${type}[^#] | wc -l)

	return 0
}

added=$(countdiff domains.txt +)
deleted=$(countdiff domains.txt -)

logmsg="Random changes"
if [ $added -gt 0 ]; then
	if [ $deleted -gt 0 ]; then
		logmsg="Added $added and deleted $deleted domains"
	else
		logmsg="Added $added domains"
	fi
elif [ $deleted -gt 0 ]; then
	logmsg="Deleted $deleted domains"
fi

git add .
git commit -m "$logmsg"
git push
