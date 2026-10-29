@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_EXE=%~dp0..\apiario-rocha-backend-py311\Scripts\python.exe"
set "APP_URL=http://localhost:8001"

if not exist "%PYTHON_EXE%" (
    echo.
    echo ERRO: ambiente Python local nao encontrado.
    echo Verifique se a pasta "apiario-rocha-backend-py311" existe dentro deste projeto.
    echo.
    pause
    exit /b 1
)

start "" "%APP_URL%"

echo Iniciando Apiario Rocha...
"%PYTHON_EXE%" -m uvicorn src.main:app --host 0.0.0.0 --port 8001

pause
