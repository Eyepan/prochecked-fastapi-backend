# Run MySQL
Start-Process -FilePath "mysqld" -ArgumentList "--console" -NoNewWindow

Start-Sleep -Seconds 5
# Activate virtual environment
$activatePath = "venv/Scripts/activate.ps1"
if (Test-Path $activatePath) {
    & $activatePath
} else {
    Write-Host "Virtual environment activation script not found."
}

# Run Python app
$pythonPath = "."
if (Test-Path "$pythonPath/droptables.py") {
    python "$pythonPath/droptables.py"
} else {
    Write-Host "Python app not found."
}
