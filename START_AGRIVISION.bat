@echo off
setlocal
cd /d "%~dp0"
if not exist "backend\.venv\Scripts\python.exe" (
 echo Setup is required first. Run SETUP_WINDOWS.ps1 using PowerShell.
 pause
 exit /b 1
)
if not exist "frontend-html\node_modules" (
 echo Frontend setup is required first. Run SETUP_WINDOWS.ps1 using PowerShell.
 pause
 exit /b 1
)
start "Agrivision Django Backend" /D "%~dp0backend" cmd /k ".venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000"
start "Agrivision Frontend" /D "%~dp0frontend-html" cmd /k "npm.cmd run dev"
echo Two server windows started. Visit http://localhost:5173
pause
