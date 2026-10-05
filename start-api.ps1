<#!
.SYNOPSIS
Starts the Rosas Eternas FastAPI development server on port 800.

.DESCRIPTION
Stops before launch with a clear message if another program already owns the
port. It does not terminate any process automatically.
#>
param(
    [int]$Port = 800
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'

if (!(Test-Path $python)) {
    throw 'No se encontró .venv. Ejecute: python -m venv .venv; .\.venv\Scripts\Activate.ps1; python -m pip install -r requirements.txt'
}

$listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
    Select-Object -First 1
if ($listener) {
    $processInfo = Get-Process -Id $listener.OwningProcess -ErrorAction SilentlyContinue
    throw "El puerto $Port ya está ocupado por $($processInfo.ProcessName) (PID $($listener.OwningProcess)). Detenga esa instancia o use otro puerto."
}

Set-Location $projectRoot
& $python -m uvicorn app.main:app --host 0.0.0.0 --port $Port --env-file .env
