@echo off

set DIR=%~dp0
set PATH=%PATH%;%DIR%
set PYTHONPATH=%PYTHONPATH%;%DIR%/../pylib

IF "%1"=="" (
    start cmd
) ELSE (
    REM needed for some reason
    %*
)

