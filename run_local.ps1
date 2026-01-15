# Local Django development startup script for PowerShell

Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Metateks - Local Django Development" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "Virtual environment created." -ForegroundColor Green
}

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements-pip.txt

# Load .env.local for local development
$envFile = ".env.local"
if (Test-Path $envFile) {
    Write-Host "Loading environment from $envFile..." -ForegroundColor Yellow
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $name = $matches[1]
            $value = $matches[2]
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
            Write-Host "  $name = $value" -ForegroundColor Gray
        }
    }
}

# Create logs directory if not exists
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Run migrations
Write-Host ""
Write-Host "Running migrations..." -ForegroundColor Yellow
python manage.py migrate

# Collect static files
Write-Host ""
Write-Host "Collecting static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput

# Start development server
Write-Host ""
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Starting Django development server" -ForegroundColor Green
Write-Host "URL: http://localhost:8000" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Cyan
python manage.py runserver
