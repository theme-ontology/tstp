@echo off

setlocal
set DIR=%~dp0
set PATH=D:\Applications\Python37;D:\Applications\Python37\Scripts;%PATH%;%DIR%
set PYTHONPATH=%PYTHONPATH%;%DIR%\..\pylib

IF "%1"=="" (
    start cmd
) ELSE (
    REM needed for some reason
    %*
)

