# g.ps1 (Supreme Integrated Hub V10.0 - Eternal Strategy)
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (-not $PROJECT_ROOT) { $PROJECT_ROOT = (Get-Location).Path }
Set-Location $PROJECT_ROOT

$pythonExe = Join-Path $PROJECT_ROOT ".venv\Scripts\python.exe"
$webDir = Join-Path $PROJECT_ROOT "web"
$dashDir = Join-Path $PROJECT_ROOT "dashboard"

Clear-Host
Write-Host "=========================================================" -ForegroundColor Green
Write-Host "   SUPREME COUNCIL COMMAND CENTER V10.0 ACTIVE" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Green

# 1. API 서버 (방송국) 가동
Write-Host "[1/4] Starting Supreme API Server (Port 5000)..." -ForegroundColor Cyan
Start-Process -FilePath $pythonExe -ArgumentList "data/agents/dashboard_api.py" -WorkingDirectory $PROJECT_ROOT -WindowStyle Hidden

Start-Sleep -Seconds 2

# 2. 4인 에이전트 가동
Write-Host "[2/4] Deploying 4 Supreme Agents (Watcher, Guardian, Debater, Inspector)..." -ForegroundColor Cyan
$agents = @("watcher.py", "guardian.py", "inspector.py", "debater.py")
foreach ($agent in $agents) {
    Start-Process -FilePath $pythonExe -ArgumentList "data/agents/$agent" -WorkingDirectory $PROJECT_ROOT -WindowStyle Hidden
}

# 3. 사령부 대시보드 가동 (Port 9999)
Write-Host "[3/4] Launching AI Strategic Dashboard (Port 9999)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoProfile", "-ExecutionPolicy Bypass", "-Command", "cd '$dashDir'; npm run dev" -WorkingDirectory $dashDir

# 4. 서비스 뷰 가동 (Port 5173)
Write-Host "[4/4] Launching Customer Service View (Port 5173)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoProfile", "-ExecutionPolicy Bypass", "-Command", "cd '$webDir'; npm run dev" -WorkingDirectory $webDir

Write-Host "`n✅ STRATEGY ECOSYSTEM DEPLOYED SUCCESSFULLY." -ForegroundColor Green
Write-Host "---------------------------------------------------------" -ForegroundColor Green
Write-Host ">>> ALL COMMANDS ARE NOW HANDLED VIA DASHBOARD (PORT 9999)." -ForegroundColor Yellow
Write-Host "---------------------------------------------------------`n" -ForegroundColor Green

# Gemini CLI 진입 (터미널은 실행 로그용으로 유지)
try { npx @google/gemini-cli } catch { Read-Host "Error: $($_)" }
