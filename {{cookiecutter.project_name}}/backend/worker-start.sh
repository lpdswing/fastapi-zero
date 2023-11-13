#! /usr/bin/env bash
set -e

python /app/backend_pre_start.py

taskiq worker src.lib.taskiq.tkq:broker
