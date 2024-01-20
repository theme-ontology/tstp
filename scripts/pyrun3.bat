@echo off

set DIR=%~dp0
set PATH=D:\Applications\Python37;D:\Applications\Python37\Scripts;%PATH%;%DIR%
set PYTHONPATH=%DIR%\..\py3lib;%DIR%\..\pylib;%PYTHONPATH%
set TSTPPATH=%DIR%..


IF "%1"=="" (
    start python
) ELSE (
    python -c "import %1; r=%1.main();" %*
)


