param(
    [switch]$InstallOnly
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $root "apiario-rocha-backend"
$venvDirectory = Join-Path $root ".venv"
$venvPython = Join-Path $venvDirectory "Scripts\python.exe"
$requirements = Join-Path $backend "requirements.txt"
$envFile = Join-Path $backend ".env"

if (-not (Test-Path $requirements)) {
    throw "Arquivo de dependências não encontrado: $requirements"
}

if (-not (Test-Path $venvPython)) {
    $pythonExe = $null
    $pythonArgs = @()
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        $pythonExe = $launcher.Source
        $pythonArgs = @("-3.11")
    }
    else {
        $launcher = Get-Command python -ErrorAction SilentlyContinue
        if ($launcher) {
            $pythonExe = $launcher.Source
        }
    }

    $workspacePython = Join-Path $root "..\apiario-rocha-backend-py311\Scripts\python.exe"
    if (
        (Test-Path $workspacePython) -and
        (-not $pythonExe -or $pythonExe -like "*\Microsoft\WindowsApps\python.exe")
    ) {
        $pythonExe = (Resolve-Path $workspacePython).Path
    }
    if (-not $pythonExe) {
        throw "Python 3.11 não encontrado. Instale o Python 3.11 e tente novamente."
    }

    $pythonVersion = & $pythonExe @pythonArgs --version 2>&1
    if ($LASTEXITCODE -ne 0 -or $pythonVersion -notmatch "Python 3\.11(\.|$)") {
        throw "Python 3.11 é necessário. Versão encontrada: $pythonVersion"
    }

    & $pythonExe @pythonArgs -m venv $venvDirectory
    if ($LASTEXITCODE -ne 0) {
        throw "Não foi possível criar o ambiente Python."
    }
}

$setupMarker = Join-Path $root ".dependencies-installed"
if (-not (Test-Path $setupMarker)) {
    & $venvPython -m pip install --disable-pip-version-check -r $requirements
    if ($LASTEXITCODE -ne 0) {
        throw "A instalação das dependências falhou. Verifique a conexão com a internet e tente novamente."
    }
    New-Item -ItemType File -Path $setupMarker -Force | Out-Null
}

if (-not (Test-Path $envFile)) {
    $randomBytes = New-Object byte[] 32
    $randomGenerator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $randomGenerator.GetBytes($randomBytes)
    }
    finally {
        $randomGenerator.Dispose()
    }
    $secretKey = [BitConverter]::ToString($randomBytes).Replace("-", "").ToLowerInvariant()
    $envContent = @"
APP_NAME=Apiário Rocha 4.0
COMPANY_NAME=Apiário Rocha
SQLITE_PATH=../data/apiario.db
SECRET_KEY=$secretKey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
"@
    [System.IO.File]::WriteAllText(
        $envFile,
        $envContent,
        [System.Text.UTF8Encoding]::new($false)
    )
}

if ($InstallOnly) {
    Write-Host "Instalação concluída. Execute iniciar.bat para abrir o sistema."
    exit 0
}

Write-Host "Iniciando Apiário Rocha em http://127.0.0.1:8001"
Start-Process "http://127.0.0.1:8001"
Push-Location $backend
try {
    & $venvPython -m uvicorn src.main:app --host 127.0.0.1 --port 8001
    if ($LASTEXITCODE -ne 0) {
        throw "O servidor terminou com erro (código $LASTEXITCODE)."
    }
}
finally {
    Pop-Location
}
