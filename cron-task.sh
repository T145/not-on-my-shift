#!/bin/bash -e
cd "$(dirname "$0")"
./bot/bot.py
./commit.sh

