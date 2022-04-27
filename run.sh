#!/bin/bash

# TODO: Test

# Only run script if on a Mac
if [[ $OSTYPE == 'darwin'* ]]; then
  # cd to this script's dir
  SCRIPT_DIR="$( dirname -- "${BASH_SOURCE[0]}" )"
  cd $SCRIPT_DIR

  # check if venv present
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
  python config.py
  BOT_PATH="$(grep -o '"bot_path": "[^"]*' init.json | grep -o '[^"]*$')"
  python $BOT_PATH
else
  echo Error: This script can only be run on a MacOS
  read -p "Press [ENTER] to close ..."
fi
