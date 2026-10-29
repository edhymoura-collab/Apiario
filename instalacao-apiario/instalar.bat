@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar.ps1" -InstallOnly
if errorlevel 1 (
    echo.
    echo A instalacao nao foi concluida. Consulte a mensagem acima.
    pause
    exit /b 1
)
pause
