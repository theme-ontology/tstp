@echo off

IF "%1"=="" (
    start python
) ELSE (
    python -c "import %1; r=%1.main();" %*
)


