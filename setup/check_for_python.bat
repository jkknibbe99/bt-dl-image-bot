@echo off

:: Check for Python Installation
python --version > NUL
if errorlevel 1 goto errorNoPython

:: Reaching here means Python is installed.
echo Python installed
goto:eof

:: Python not installed
:errorNoPython
echo Python not installed
echo Installing now...
Powershell.exe -File %~dp0setup_scripts\download_python.ps1