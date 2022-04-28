@ECHO OFF

:: Install Python if necessary
echo Checking for Python...
call %~dp0setup/check_for_python.bat && (
    rem Python installed
) || (
    echo Program shutting down
    pause
    goto:eof
)

:: Set up configuration files/data
if not exist %~dp0data (
    mkdir %~dp0data
)
if not exist %~dp0data/user_data.json (
    echo Asking for User Data...
    python %~dp0bot/config.py
)

cls

rem Set bot_path
set bot_path=%~dp0bot/bot.py

rem check if a venv exists
if exist Scripts (
    echo Scripts directory exists
    echo Running bot
    call %~dp0Scripts/activate
    rem run bot
    python %bot_path%
) else (
    echo Virtual environment not created.
    echo Creating Virtual environment now...
    python -m venv .
    if exists Scripts (
        call %~dp0Scripts/activate
        pip install -r setup/requirements.txt
        rem run bot
        python %bot_path%
    ) else (
        echo Venv creation failed.
        echo Notify Developer
        pause
    )
)