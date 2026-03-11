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

# --- 0. 기존 좀비 프로세스 청소 (MAX PURGE) ---
Write-Host "[0/5] Maximum Purge: Cleaning existing project processes..." -ForegroundColor Yellow

# 현재 파워쉘 및 부모(Gemini CLI) PID 확보
$currentPid = $PID
$parentPid = (Get-CimInstance Win32_Process -Filter "ProcessId = $currentPid").ParentProcessId
$grandParentPid = (Get-CimInstance Win32_Process -Filter "ProcessId = $parentPid").ParentProcessId

# 1. 프로젝트 경로 기반 파이썬 에이전트 정밀 타격
Get-CimInstance Win32_Process | Where-Object { 
    $_.Name -eq "python.exe" -and 
    ($_.CommandLine -like "*$PROJECT_ROOT*" -or $_.ExecutablePath -like "*$PROJECT_ROOT*") -and
    $_.ProcessId -ne $currentPid -and $_.ProcessId -ne $parentPid -and $_.ProcessId -ne $grandParentPid
} | ForEach-Object {
    Write-Host "Terminating Zombie Agent (PID: $($_.ProcessId))..." -ForegroundColor Gray
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}

# 2. 포트 점유 프로세스 강제 해제 (Dashboard: 9999, Web: 5173, Hub: 5055)
# (포트 기반은 안전하므로 유지하되, 현재 세션 포트는 건드리지 않음)
@(9999, 5173, 5055) | ForEach-Object {
    $port = $_
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connections) {
        $connections | ForEach-Object {
            if ($_.OwningProcess -gt 0 -and $_.OwningProcess -ne $parentPid -and $_.OwningProcess -ne $grandParentPid) {
                Write-Host "Releasing Port $port (Zombie PID: $($_.OwningProcess))..." -ForegroundColor Gray
                Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

# 3. 잔여 Node 프로세스 (Vite 관련) 정리 - 특정 경로(dashboard, web)만 타격하여 '나'를 보호
Get-CimInstance Win32_Process | Where-Object { 
    $_.Name -eq "node.exe" -and 
    ($_.CommandLine -like "*vite*" -or $_.CommandLine -like "*npm*") -and 
    ($_.CommandLine -like "*dashboard*" -or $_.CommandLine -like "*web*") -and
    $_.ProcessId -ne $currentPid -and $_.ProcessId -ne $parentPid -and $_.ProcessId -ne $grandParentPid
} | ForEach-Object {
    Write-Host "Terminating Zombie Node (PID: $($_.ProcessId))..." -ForegroundColor Gray
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 1

# --- 1. 가용한 파이썬 엔진 탐색 ---
$potentialPythons = @("python.exe", "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe", "C:\Users\pc\AppData\Local\Python\pythoncore-3.14-64\python.exe")
$basePython = $null
foreach ($pyPath in $potentialPythons) {
    try { & $pyPath --version 2>$null; if ($lastExitCode -eq 0) { $basePython = $pyPath; break } } catch {}
}

# --- 2. 가상환경 진단 (PORTABLE SELF-HEALING) ---
Write-Host "[2/5] Diagnostic: Checking required packages..." -ForegroundColor Cyan
# 패키지명과 실제 임포트명이 다른 경우를 위한 맵핑
$pkgCheck = @{
    "fastapi" = "fastapi"
    "uvicorn" = "uvicorn"
    "python-socketio" = "socketio"
    "google-genai" = "google.genai"
    "python-dotenv" = "dotenv"
}
$missingPackages = @()

foreach ($pkg in $pkgCheck.Keys) {
    $importName = $pkgCheck[$pkg]
    & $venvPython -c "import $importName" 2>$null
    if ($lastExitCode -ne 0) { $missingPackages += $pkg }
}

if ($missingPackages.Count -gt 0) {
    Write-Host "[!] Missing packages detected: $($missingPackages -join ', ')" -ForegroundColor Yellow
    Write-Host "[!] Starting automatic repair in current environment..." -ForegroundColor Cyan
    & $venvPython -m pip install --upgrade pip
    foreach ($pkg in $missingPackages) {
        Write-Host "Installing $pkg..." -ForegroundColor Gray
        & $venvPython -m pip install $pkg
    }
    Write-Host "✅ Environment repair complete." -ForegroundColor Green
} else {
    Write-Host "✅ All required packages found." -ForegroundColor Green
}

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
`$agents = @("liaison_v15.py", "planner_v15.py", "watcher_v15.py", "safety_guard_v15.py", "inspector_v15.py", "terminal_nerve.py")
foreach (`$agent in `$agents) {
    Write-Host "Launching Agent: `$agent" -ForegroundColor Cyan
    # 조율자와 터미널 신경망은 실시간 감시를 위해 창을 띄움
    if (`$agent -eq "liaison_v15.py" -or `$agent -eq "terminal_nerve.py") {
        Start-Process -FilePath '$venvPython' -ArgumentList "data/agents/`$agent" -WorkingDirectory '$PROJECT_ROOT' -WindowStyle Normal
    } else {
        Start-Process -FilePath '$venvPython' -ArgumentList "data/agents/`$agent" -WorkingDirectory '$PROJECT_ROOT' -WindowStyle Hidden
    }
    Start-Sleep -Seconds 1
}

Write-Host "--- [STAGE 3] HUB ACTIVATION (FASTAPI-ASGI) ---" -ForegroundColor Green
try {
    & '$venvPython' "data/agents/dashboard_api.py"
} catch {
    Write-Host "`n[!] CRITICAL ERROR in Nerve Hub: `$(`$_.Exception.Message)" -ForegroundColor Red
    Pause
} finally {
    Write-Host "`n[!] SHUTDOWN SIGNAL RECEIVED. Surgical cleanup in progress..." -ForegroundColor Red
    
    # 1. 프로젝트 관련 브라우저 탭만 정밀 종료
    Get-Process | Where-Object { `$_.MainWindowTitle -like '*FREEISM*' -or `$_.MainWindowTitle -like '*SUPREME COUNCIL*' } | ForEach-Object {
        Write-Host "Closing Project Tab: `$(`$_.MainWindowTitle)" -ForegroundColor Gray
        `$_.CloseMainWindow() | Out-Null
    }

    # 2. 프로젝트 전용 파이썬 에이전트 정밀 사살 (Surgical Kill)
    # 시스템의 다른 파이썬은 건드리지 않고, 이 프로젝트 폴더 내에서 실행된 것만 잡음
    Write-Host "Hunting background agents in '$PROJECT_ROOT'..." -ForegroundColor Yellow
    Get-CimInstance Win32_Process | Where-Object { 
        `$_.Name -eq "python.exe" -and (`$_.CommandLine -like "*$PROJECT_ROOT*" -or `$_.ExecutablePath -like "*$PROJECT_ROOT*")
    } | ForEach-Object {
        Write-Host "Terminating Agent PID: `$(`$_.ProcessId)" -ForegroundColor Gray
        Stop-Process -Id `$_.ProcessId -Force -ErrorAction SilentlyContinue
    }
    
    # 3. 포트 강제 해제 (9999: Dashboard, 5173: Web, 5055: Hub)
    @(9999, 5173, 5055) | ForEach-Object {
        `$p = (Get-NetTCPConnection -LocalPort `$_ -ErrorAction SilentlyContinue).OwningProcess
        if (`$p) { 
            Write-Host "Releasing Port `$_ (PID: `$p)..." -ForegroundColor Gray
            Stop-Process -Id `$p -Force -ErrorAction SilentlyContinue 
        }
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
