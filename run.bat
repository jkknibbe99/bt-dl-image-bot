@ECHO OFF


:: Run python config file
python %~dp0bot\config.py

:: Make it possible to read immediate value of variable using !variable! syntax.
setlocal enabledelayedexpansion

:: Read file "init.json" into variable data
set data=
for /f "delims=" %%x in (%~dp0data/init.json) do set "data=!data!%%x"
rem Remove quotes
set data=%data:"=%
rem Remove braces
set "data=%data:~2,-1%"
rem Change colon+space to equal-sign
set "data=%data:: ==%"
rem Separate parts at comma into individual assignments
set "%data:, =" & set "%"

cls

rem Set bot_path
set bot_path=%~dp0%bot_path:/=\%

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
