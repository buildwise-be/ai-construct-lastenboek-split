@echo off
REM Windows batch script to view AI Construct PDF Opdeler logs
REM 
REM Usage:
REM   view_logs.bat         - View latest log
REM   view_logs.bat follow  - Follow latest log in real-time
REM   view_logs.bat list    - List all log files

if "%1"=="follow" (
    echo 🔄 Following latest log file...
    python view_logs.py --follow
) else if "%1"=="list" (
    python view_logs.py --list
) else if "%1"=="help" (
    echo.
    echo AI Construct PDF Opdeler - Log Viewer
    echo =====================================
    echo.
    echo Usage:
    echo   view_logs.bat         - View latest log
    echo   view_logs.bat follow  - Follow latest log in real-time
    echo   view_logs.bat list    - List all log files
    echo   view_logs.bat help    - Show this help
    echo.
) else (
    echo 📖 Viewing latest log file...
    python view_logs.py
)

pause 