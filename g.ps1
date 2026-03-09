# g.ps1 (Supreme Integrated Hub V14.1 - USB-Portable Architecture)
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (-not $PROJECT_ROOT) { $PROJECT_ROOT = (Get-Location).Path }
Set-Location $PROJECT_ROOT

$pythonExe = Join-Path $PROJECT_ROOT ".venv\Scripts\python.exe"
$dashDir = Join-Path $PROJECT_ROOT "dashboard"
$webDir = Join-Path $PROJECT_ROOT "web"
$portFile = Join-Path $PROJECT_ROOT "data\port.txt"

Clear-Host
Write-Host "=========================================================" -ForegroundColor Green
Write-Host "   SUPREME COUNCIL COMMAND CENTER V14.1 (USB-READY)" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Green

# 1. 신경 허브 (Hub) 가동 및 빈 포트 탐색
Write-Host "[1/6] Searching for Free Nerve Port (Hub Startup)..." -ForegroundColor Cyan
Start-Process -FilePath $pythonExe -ArgumentList "data/agents/dashboard_api.py" -WorkingDirectory $PROJECT_ROOT -WindowStyle Hidden

# 2. 포트 확정 대기 및 읽기
Write-Host "[2/6] Waiting for Hub to claim a Port..." -ForegroundColor Cyan
$maxRetries = 10
$activePort = "5055" # Default fallback
for ($i=0; $i -lt $maxRetries; $i++) {
    if (Test-Path $portFile) {
        $activePort = (Get-Content $portFile).Trim()
        if ($activePort) { break }
    }
    Start-Sleep -Seconds 1
}
Write-Host "✅ HUB SUCCESSFULLY CLUTCHED PORT: $activePort" -ForegroundColor Green

# 3. 5대 독립 에이전트 군단 가동 (가상환경 독립 프로세스)
Write-Host "[3/6] Deploying 5 Independent Agents (VIRTUAL NERVE)..." -ForegroundColor Cyan
$agents = @("main_ai_v14.py", "watcher_v14.py", "guardian_v14.py", "inspector_v14.py", "debater_v14.py")
foreach ($agentFile in $agents) {
    Write-Host " -> Launching $agentFile (Connecting to $activePort)..." -ForegroundColor Gray
    Start-Process -FilePath $pythonExe -ArgumentList "data/agents/$agentFile" -WorkingDirectory $PROJECT_ROOT -WindowStyle Hidden
}

# 4. 사령부 대시보드 가동 (Port 9999) - 동적 포트 주입
Write-Host "[4/6] Launching AI Strategic Dashboard (Port 9999)..." -ForegroundColor Cyan
# 환경변수 주입을 위해 $env: 활용
$env:VITE_SOCKET_PORT = $activePort
Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass", "-Command", "cd '$dashDir'; `$env:VITE_SOCKET_PORT='$activePort'; npm run dev -- --port 9999" -WorkingDirectory $dashDir

# 5. 서비스 뷰 가동 (Port 5173)
Write-Host "[5/6] Launching Customer Service View (Port 5173)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass", "-Command", "cd '$webDir'; npm run dev -- --port 5173" -WorkingDirectory $webDir

Write-Host "`n✅ NEURAL ECOSYSTEM V14.1 DEPLOYED SUCCESSFULLY." -ForegroundColor Green
Write-Host "---------------------------------------------------------" -ForegroundColor Green
Write-Host ">>> DYNAMIC HUB PORT: $activePort" -ForegroundColor Yellow
Write-Host ">>> ALL 5 AGENTS ARE NOW INDEPENDENT AND CONNECTED." -ForegroundColor Yellow
Write-Host ">>> USB PORTABILITY: ACTIVE (ROOT-RELATIVE ADDRESSING)." -ForegroundColor Cyan
Write-Host "---------------------------------------------------------`n" -ForegroundColor Green

Write-Host ">>> Terminal is standing by for system logs. Press Ctrl+C to exit." -ForegroundColor Gray
while($true) { Start-Sleep -Seconds 60 }
