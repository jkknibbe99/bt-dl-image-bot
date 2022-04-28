@echo off

cls
echo Checking for python...

:: Check for Python Installation
python --version && (
rem python installed
) || (
goto:errorNoPython
)

:: Reaching here means Python is installed.
echo Python installed
goto:eof

:: Python not installed
:errorNoPython
echo Python not installed
echo Installing now...
Powershell.exe -File %~dp0download_python.ps1 && (
    Echo Python download script successful
) || (
    echo Python download script failure
    echo Notify Developer
    pause
    EXIT /b 1
)

:: Wait until python installed
:START
if not exist "c:\Program Files (x86)\Python3.10.4\python.exe" GOTO WAIT
goto:DONE

:WAIT
:: pause for 1 second
cls
echo Waiting for Python to begin installing...
ping 127.0.0.1 > nul
goto:START

:DONE
cls
echo Wait until the Python installer is complete.
echo Once it is,
pause
