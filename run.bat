@ECHO OFF

cls

rem Set bot_path
set bot_path=%~dp0bot\bot.py

rem check if a venv exists
if exist Scripts (
    echo Scripts directory exists
    echo Running bot
    call %~dp0Scripts\activate
    rem run bot
    python %bot_path%
) else (
    echo Virtual environment not created.
    echo Creating Virtual environment now...
    python -m venv .
    call %~dp0Scripts\activate
    pip install -r requirements.txt
    rem run bot
    python %bot_path%
)
