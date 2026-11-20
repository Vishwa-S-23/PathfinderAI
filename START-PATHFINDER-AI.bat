@echo off
setlocal
cd /d "%~dp0"

if not exist "runtime\python\python.exe" (
  echo This portable package is incomplete: runtime\python\python.exe is missing.
  pause
  exit /b 1
)

"runtime\python\python.exe" "app\launcher.py"
set "PATHFINDER_EXIT=%ERRORLEVEL%"
if not "%PATHFINDER_EXIT%"=="0" pause
exit /b %PATHFINDER_EXIT%