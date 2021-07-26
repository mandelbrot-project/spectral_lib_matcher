#!/usr/bin/env bash

if [[ ! -f setup.py ]]; then
  echo "Sorry, you have to run this script from the root directory of the project."
  exit 1
fi

pip install -e .

python -m pytest