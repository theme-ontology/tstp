@echo off
setlocal

set DIR=%~dp0
set PATH=%PATH%;%DIR%
set PYTHONPATH=%PYTHONPATH%;%DIR%\..\pylib
set TSTPPATH=%DIR%..

for /f "tokens=1,* delims= " %%a in ("%*") do set ALL_BUT_FIRST=%%b

python -m unittest %*


