#!/bin/bash -e

set -e
set -o pipefail

cd "$(dirname "$0")"

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

if [ $added -gt 0 ]; then
	if [ $deleted -gt 0 ]; then
		logmsg="Added $added and deleted $deleted domains"
	else
		logmsg="Added $added domains"
	fi
elif [ $deleted -gt 0 ]; then
	logmsg="Deleted $deleted domains"
else
	echo "No changes to domains - aborting"
	exit 0
fi

git add domains.txt
git commit -m "$logmsg"
git push
