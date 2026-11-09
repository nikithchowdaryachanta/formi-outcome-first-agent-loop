#!/usr/bin/env bash
set -euo pipefail

SIM_URL="${1:?Usage: ./run.sh <SIM_URL>}"

echo "Starting Formi autonomous controller..."
exec python controller.py "$SIM_URL"
