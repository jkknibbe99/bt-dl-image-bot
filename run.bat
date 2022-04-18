@ECHO OFF

:: Run python config file
python config.py

:: Make it possible to read immediate value of variable using !variable! syntax.
setlocal enabledelayedexpansion

:: Read file "init.json" into variable data
set data=
for /f "delims=" %%x in (init.json) do set "data=!data!%%x"
rem Remove quotes
set data=%data:"=%
rem Remove braces
set "data=%data:~2,-1%"
rem Change colon+space to equal-sign
set "data=%data:: ==%"
rem Separate parts at comma into individual assignments
set "%data:, =" & set "%"

cls

rem check if a venv exists
if exist Scripts (
    echo Scripts directory exists
    echo Running bot
    call Scripts\activate
    rem run bot
    set bot_path=%bot_path:/=\%
    python %bot_path%
) else (
    echo Virtual environment not created.
    echo Creating Virtual environment now...
    python -m venv .
    call Scripts\activate
    pip install -r requirements.txt
    rem run bot
    set bot_path=%bot_path:/=\%
    python %bot_path%
)
