#!/bin/bash

if [[ ! -d python-env ]]; then
  python3 -m venv python-env
  . python-env/bin/activate
  pip3 install -r Requirements.txt
else
  . python-env/bin/activate
fi


