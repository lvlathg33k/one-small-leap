#!/usr/bin/env bash
# Idempotent dependency setup for the "One Small Leap" Streamlit app.
set -euo pipefail

cd "$(dirname "$0")/.."

# The default base image ships Python 3.12 but not the venv/ensurepip module,
# which is required to create an isolated virtualenv.
if ! python3 -c "import ensurepip" >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo apt-get install -y -qq python3.12-venv
fi

# Create (or reuse) an isolated virtualenv and refresh dependencies.
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

echo "install.sh: dependencies ready ($(.venv/bin/streamlit --version))"
