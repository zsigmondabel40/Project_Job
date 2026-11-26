@echo off
REM Stop the daily 10:00 refresh. Double-click this file.
REM It only removes the schedule; nothing in the project is deleted.

setlocal
set "TASKNAME=Project_job daily refresh"

schtasks /delete /tn "%TASKNAME%" /f

if errorlevel 1 (
    echo.
    echo No such scheduled task - it was probably never installed.
) else (
    echo.
    echo Removed. The job data will no longer refresh by itself.
    echo You can still refresh whenever you like by double-clicking
    echo scripts\refresh_daily.bat
)

echo.
pause
