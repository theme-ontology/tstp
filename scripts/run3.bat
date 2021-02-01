@echo off

setlocal
set DIR=%~dp0
set PATH=D:\Applications\Python37;D:\Applications\Python37\Scripts;%PATH%;%DIR%
set PYTHONPATH=%DIR%\..\py3lib;%DIR%\..\pylib;%PYTHONPATH%

IF "%1"=="" (
    start cmd
) ELSE (
    REM needed for some reason
    %*
)

