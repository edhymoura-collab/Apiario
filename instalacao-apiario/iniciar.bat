@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar.ps1"
if errorlevel 1 (
    echo.
    echo O sistema nao conseguiu iniciar. Consulte a mensagem acima.
    pause
    exit /b 1
)
