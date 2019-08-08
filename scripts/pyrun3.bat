@echo off

set DIR=%~dp0
set PATH=D:\Applications\Python37;D:\Applications\Python37\Scripts;%PATH%;%DIR%
set PYTHONPATH=%PYTHONPATH%;%DIR%\..\pylib
set TSTPPATH=%DIR%..


IF "%1"=="" (
    start python
) ELSE (
    python -c "import %1; r=%1.main();" %*
)


