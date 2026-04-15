$venvPath = ".\.venv"

if (Test-Path "$venvPath\Scripts\python.exe") {
    Write-Host "venv already exists, skipping" -ForegroundColor Green
} else {
    Write-Host "Creating venv..." -ForegroundColor Cyan
    python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) { Write-Host "Failed to create venv" -ForegroundColor Red; exit 1 }
    Write-Host "Installing from requirements.txt..." -ForegroundColor Cyan
    & "$venvPath\Scripts\pip" install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { Write-Host "Install failed" -ForegroundColor Red; exit 1 }
    Write-Host "Done" -ForegroundColor Green
}
Write-Host "Python: $venvPath\Scripts\python.exe" -ForegroundColor Yellow