@echo off
REM ---------------------------------------------------------------------
REM  Tell Windows to refresh the job data every day at 10:00.
REM  Double-click this file once. No administrator rights needed.
REM
REM  To remove it later, double-click uninstall_daily_task.bat, or run:
REM      schtasks /delete /tn "Project_job daily refresh" /f
REM ---------------------------------------------------------------------

setlocal
set "TASKNAME=Project_job daily refresh"
set "RUNME=%~dp0refresh_daily.bat"

echo Creating the scheduled task "%TASKNAME%"
echo It will run:  %RUNME%
echo Every day at: 10:00
echo.

schtasks /create /tn "%TASKNAME%" /tr "\"%RUNME%\"" /sc daily /st 10:00 /f

if errorlevel 1 (
    echo.
    echo Could not create the task. Try opening Task Scheduler yourself:
    echo   Start menu -^> Task Scheduler -^> Create Basic Task
    echo   Trigger: Daily, 10:00.  Action: Start a program.
    echo   Program: %RUNME%
) else (
    echo.
    echo Done. Two things worth knowing:
    echo.
    echo  1. Your PC must be switched on and awake at 10:00. If it is off,
    echo     Windows skips that day. To make it catch up instead, open Task
    echo     Scheduler, find "%TASKNAME%", Properties -^> Settings, and tick
    echo     "Run task as soon as possible after a scheduled start is missed".
    echo.
    echo  2. Each run appends to logs\refresh.log, so you can check later
    echo     whether it worked.
)

echo.
pause
