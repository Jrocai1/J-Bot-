@echo off
setlocal EnableExtensions
title J-Bot Agent Fixer
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo [J-Bot] Python 3.12 or newer is required.
  echo Install Python from https://www.python.org/downloads/windows/
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo [J-Bot] Creating a local Python environment...
  py -3 -m venv .venv
  if errorlevel 1 goto :failed
)
echo [J-Bot] Installing free/open-source runtime dependencies...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto :failed
echo [J-Bot] Starting the local dashboard and diagnostic API...
".venv\Scripts\python.exe" core_engine.py
if errorlevel 1 goto :failed
goto :eof
:failed
echo.
echo [J-Bot] Startup failed. Read the error above; no diagnostic repair was executed.
pause
exit /b 1
