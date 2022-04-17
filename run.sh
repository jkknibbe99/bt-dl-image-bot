#!/bin/bash

SCRIPT_DIR="$( dirname -- "${BASH_SOURCE[0]}" )"
# SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd $SCRIPT_DIR

BIN_DIR="$SCRIPT_DIR/bin/"
if [ -d "$BIN_DIR" ]; then
  ### virtual env bin dir was found ###
  echo "Venv found."
  source bin/activate
else
  ### create virtual environment if one does not already exist ###
  echo "No venv found. Creating one now."
  virtualenv --python=python3 .
  source bin/activate
  pip install -r requirements.txt
fi

# make chrome driver executable
chmod +x chromedriver_100_mac

# run bot
python bot.py 