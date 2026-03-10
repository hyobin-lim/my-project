# g.ps1 (Supreme Integrated Hub V14.7 - Surgical Shutdown)
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (-not $PROJECT_ROOT) { $PROJECT_ROOT = (Get-Location).Path }
Set-Location $PROJECT_ROOT

$dashDir = Join-Path $PROJECT_ROOT "dashboard"
$webDir = Join-Path $PROJECT_ROOT "web"
$venvDir = Join-Path $PROJECT_ROOT ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"

Clear-Host
Write-Host "=========================================================" -ForegroundColor Green
Write-Host "   SUPREME COUNCIL COMMAND CENTER V14.7 (MODERN)" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Green

# --- 0. 기존 좀비 프로세스 청소 ---
Write-Host "[0/5] Cleaning existing processes..." -ForegroundColor Yellow
taskkill /F /IM python.exe /T 2>$null
taskkill /F /IM node.exe /T 2>$null
@(5055, 9999, 5173) | ForEach-Object {
    $p = (Get-NetTCPConnection -LocalPort $_ -ErrorAction SilentlyContinue).OwningProcess
    if ($p) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue }
}
Start-Sleep -Seconds 1

# --- 1. 가용한 파이썬 엔진 탐색 ---
$potentialPythons = @("python.exe", "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe", "C:\Users\pc\AppData\Local\Python\pythoncore-3.14-64\python.exe")
$basePython = $null
foreach ($pyPath in $potentialPythons) {
    try { & $pyPath --version 2>$null; if ($lastExitCode -eq 0) { $basePython = $pyPath; break } } catch {}
}

# --- 2. 가상환경 진단 (생략 - 이미 최신화됨) ---

# --- 3. 통합 부트 스크립트 생성 (PRECISION CLEANUP) ---
Write-Host "[3/5] Generating Precise Boot Script..." -ForegroundColor Cyan
$bootFile = Join-Path $PROJECT_ROOT "data\boot.ps1"

$bootContent = @"
`$Host.UI.RawUI.WindowTitle = 'SUPREME COUNCIL - MASTER HUB'
cd '$PROJECT_ROOT'

Write-Host "--- [STAGE 1] PREPARING SERVERS ---" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoProfile", "-NoExit", "-Command", "`$Host.UI.RawUI.WindowTitle = 'SERVER: DASHBOARD (9999)'; cd '$dashDir'; npm run dev -- --port 9999" -WindowStyle Hidden
Start-Process powershell -ArgumentList "-NoProfile", "-NoExit", "-Command", "`$Host.UI.RawUI.WindowTitle = 'SERVER: WEB SERVICE (5173)'; cd '$webDir'; npm run dev -- --port 5173" -WindowStyle Hidden

Write-Host "--- [STAGE 2] STARTING AI AGENTS ---" -ForegroundColor Green
`$agents = @("main_ai_v14.py", "watcher_v14.py", "guardian_v14.py", "inspector_v14.py", "debater_v14.py")
foreach (`$agent in `$agents) {
    Write-Host "Launching Agent: `$agent" -ForegroundColor Cyan
    Start-Process -FilePath '$venvPython' -ArgumentList "data/agents/`$agent" -WorkingDirectory '$PROJECT_ROOT' -WindowStyle Hidden
    Start-Sleep -Seconds 1
}

Write-Host "--- [STAGE 3] HUB ACTIVATION (FASTAPI-ASGI) ---" -ForegroundColor Green
try {
    & '$venvPython' "data/agents/dashboard_api.py"
} finally {
    Write-Host "`n[!] SHUTDOWN SIGNAL RECEIVED. Surgical cleanup in progress..." -ForegroundColor Red
    
    # 1. 브라우저 탭 정밀 종료 (프로젝트 관련 타이틀만 타격)
    Get-Process | Where-Object { `$_.MainWindowTitle -like '*FREEISM*' -or `$_.MainWindowTitle -like '*SUPREME COUNCIL*' } | ForEach-Object {
        Write-Host "Closing Browser Tab: `$(`$_.MainWindowTitle)" -ForegroundColor Gray
        `$_.CloseMainWindow() | Out-Null
    }

    # 2. 모든 파이썬 및 노드 프로세스 종료
    taskkill /F /IM python.exe /T 2>`$null
    taskkill /F /IM node.exe /T 2>`$null
    
    # 3. 포트 강제 해제
    @(9999, 5173, 5055) | ForEach-Object {
        `$p = (Get-NetTCPConnection -LocalPort `$_ -ErrorAction SilentlyContinue).OwningProcess
        if (`$p) { Stop-Process -Id `$p -Force -ErrorAction SilentlyContinue }
    }

    Write-Host "✅ System fully offline. Closing this console..." -ForegroundColor Green
    Start-Sleep -Seconds 1
    exit
}
"@

$bootContent | Out-File -FilePath $bootFile -Encoding utf8 -Force

# --- 4. 마스터 허브 실행 (NO-EXIT 제거하여 자동 종료 활성화) ---
Write-Host "[4/5] Launching Master Hub Console..." -ForegroundColor Cyan
# 여기서 -NoExit를 빼야 boot.ps1의 exit가 먹힙니다.
Start-Process powershell -ArgumentList "-NoProfile", "-ExecutionPolicy Bypass", "-File `"$bootFile`""

Write-Host "`n✅ DEPLOYMENT STARTED. Gemini CLI ready." -ForegroundColor Green
Start-Sleep -Seconds 1
