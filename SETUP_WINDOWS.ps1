$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $root 'backend'
$frontend = Join-Path $root 'frontend-html'
Write-Host '== Agrivision Windows setup ==' -ForegroundColor Green
if (-not (Get-Command py -ErrorAction SilentlyContinue)) { throw 'Python launcher py not found. Install Python 3.12 or 3.13 from python.org and enable PATH.' }
if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) { throw 'Node.js/npm not found. Install Node.js 22 or newer first.' }
Set-Location $backend
if (-not (Test-Path '.venv/Scripts/python.exe')) { py -3 -m venv .venv; if ($LASTEXITCODE -ne 0) { throw 'Python virtual environment creation failed.' } }
$python = Join-Path $backend '.venv/Scripts/python.exe'
& $python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'pip upgrade failed. Check your internet connection.' }
& $python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed. Check Python version and internet connection.' }
if (-not (Test-Path '.env')) {
    Copy-Item '.env.example' '.env'
    $secret = & $python -c "import secrets; print(secrets.token_urlsafe(48))"
    (Get-Content '.env' -Raw).Replace('replace-with-a-unique-random-secret', $secret) | Set-Content '.env' -Encoding utf8
    Write-Host 'Created backend/.env. Add your Gemini key to GEMINI_API_KEY.' -ForegroundColor Yellow
}
& $python manage.py migrate
if ($LASTEXITCODE -ne 0) { throw 'Database migration failed.' }
& $python manage.py check
if ($LASTEXITCODE -ne 0) { throw 'Django system check failed.' }
Set-Location $frontend
& npm.cmd install
if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed.' }
Write-Host 'Setup complete. Update backend/.env with your Gemini key (optional for basic results).' -ForegroundColor Green
Write-Host 'Then double-click START_AGRIVISION.bat or run it from the project folder.'
