@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher was not found. Install Python 3.12+ and enable Add Python to PATH.
  pause
  exit /b 1
)
py -3 -m jbot
echo.
pause
