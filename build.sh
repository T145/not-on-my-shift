#!/bin/bash -e
cd "$(dirname "$0")"

# Create build directory if it does not exist
[ -d build ] || mkdir build

# Add timestamp to domains
timestamp="$(git log -1 --pretty="format:%cI" domains.txt)"
sed -r "s|\{\{timestamp\}\}|${timestamp}|" domains.txt >build/domains.txt

# Convert to hosts
sed -r "s|^[a-z0-9-]+\.[a-z]+$|&\nwww.&|" build/domains.txt | sed -r "s|^([a-z0-9-]+\.)+[a-z]+$|0.0.0.0 &|" >build/hosts.txt
