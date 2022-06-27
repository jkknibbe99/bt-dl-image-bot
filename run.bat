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

:: First check for Venv
if exist %~dp0Scripts (
    echo Scripts directory exists
    echo Running bot...
    call %~dp0Scripts/activate
    python %bot_path%
    goto:EOF
) else (
    echo Virtual environment not created.
    echo Creating Virtual environment now...
    set venvpath=%~dp0
    pause
    python -m venv %venvpath%
    goto:VENV_CHECK_2
)

:: Second check for Venv
:VENV_CHECK_2
if exist %~dp0Scripts (
    echo Venv set up
    call %~dp0Scripts/activate
    echo Installing requirements...
    pip install -r %~dp0setup/requirements.txt
    cls
    echo Running bot...
    python %bot_path%
) else (
    echo Virtual environment not created.
    echo Creating Virtual environment now...
    python -m venv %~dp0
    goto:VENV_CHECK_3
)

:: Third check for Venv
:VENV_CHECK_3
if exist %~dp0Scripts (
    echo Venv set up
    call %~dp0Scripts/activate
    echo Installing requirements...
    pip install -r %~dp0setup/requirements.txt
    cls
    echo Running bot...
    python %bot_path%
) else (
    echo Venv creation failed.
    echo Notify Developer
    pause
)
