@echo off

REM Set the project root directory
set PROJECT_ROOT=c:\Code\ResponSync-1

REM Add the src directory to PYTHONPATH
set PYTHONPATH=%PROJECT_ROOT%\src;%PYTHONPATH%

REM Change to the project root directory
cd "%PROJECT_ROOT%"

REM Run main.py
python src/main.py

REM Check if main.py ran successfully
IF %ERRORLEVEL% NEQ 0 (
    echo Error: main.py failed to execute.
    goto :eof
)

REM Change to the directory where KPI.py is located (adjust path as needed)
REM Assuming KPI.py is in the same directory as main.py for this example
REM If KPI.py is in a different location, update the path accordingly.
REM For example, if KPI.py is in c:\Code\ResponSync-1\scripts\KPI.py, you would use:
REM cd "c:\Code\ResponSync-1\scripts"

REM Run KPI.py
cd "c:\Code\ResponSync-1\src\backend"
python KPI.py

IF %ERRORLEVEL% NEQ 0 (
    echo Error: KPI.py failed to execute.
    goto :eof
)

cd "c:\Code\ResponSync-1\"

echo All scripts executed successfully.