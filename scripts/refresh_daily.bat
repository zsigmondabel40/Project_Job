@echo off
REM ---------------------------------------------------------------------
REM  Refresh the job data on this Windows PC.
REM
REM  This is the file Windows Task Scheduler runs every day at 10:00.
REM  To set that up once, double-click:  scripts\install_daily_task.bat
REM
REM  You can also just double-click THIS file any time to refresh now.
REM  Everything it prints is appended to  logs\refresh.log  so you can see
REM  afterwards what happened while you were not watching.
REM ---------------------------------------------------------------------

setlocal
REM Work from the project folder, whatever folder this was launched from.
cd /d "%~dp0.."

if not exist "logs" mkdir "logs"

echo. >> "logs\refresh.log"
echo ============================================================ >> "logs\refresh.log"
echo Run started %DATE% %TIME% >> "logs\refresh.log"

where python >nul 2>&1
if errorlevel 1 (
    echo PYTHON NOT FOUND. Install Python from python.org and tick >> "logs\refresh.log"
    echo "Add python.exe to PATH" during the install, then try again. >> "logs\refresh.log"
    echo PYTHON NOT FOUND - see logs\refresh.log
    exit /b 9009
)

python "scripts\refresh_all.py" >> "logs\refresh.log" 2>&1
set RESULT=%ERRORLEVEL%

echo Run finished %DATE% %TIME% with exit code %RESULT% >> "logs\refresh.log"

REM Exit code 0 = everything refreshed. Anything else = at least one portal
REM could not be reached; the previous jobs are still in the app.
exit /b %RESULT%
