@REM @ECHO OFF

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
rem Change colon+space by equal-sign
set "data=%data:: ==%"
rem Separate parts at comma into individual assignments
set "%data:, =" & set "%"

rem check if a venv exists
if exist Scripts (
    echo Scripts Dir exists
    call Scripts\activate
    rem run bot
    python %bot_path%
) else (
    ECHO Virtual environment not created.
    ECHO Creating Virtual environment now...
    python -m venv .
    Scripts\activate
    pip install -r requirements.txt
    rem run bot
    python %bot_path%
)
