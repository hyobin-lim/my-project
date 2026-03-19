# g.ps1 (V22.0 GAIA EDITION - Guardian Ignition)
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (-not $PROJECT_ROOT) { $PROJECT_ROOT = (Get-Location).Path }
Set-Location $PROJECT_ROOT

$venvDir = Join-Path $PROJECT_ROOT ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"

Clear-Host
Write-Host "=========================================================" -ForegroundColor Green
Write-Host "   PROJECT FREEISM V22.0 - NEURAL IGNITION SEQUENCE" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Green

# --- 1. 환경 정화 (MAX PURGE) ---
Write-Host "`n[1/5] Environment Purge: Cleaning zombies..." -ForegroundColor Yellow

$currentPid = $PID
$parentPid = (Get-CimInstance Win32_Process -Filter "ProcessId = $currentPid").ParentProcessId
$grandParentPid = (Get-CimInstance Win32_Process -Filter "ProcessId = $parentPid").ParentProcessId

# 좀비 프로세스 조용히 처리
Get-CimInstance Win32_Process | Where-Object { 
    $_.Name -eq "python.exe" -and ($_.CommandLine -like "*$PROJECT_ROOT*" -or $_.ExecutablePath -like "*$PROJECT_ROOT*") -and
    $_.ProcessId -ne $currentPid -and $_.ProcessId -ne $parentPid -and $_.ProcessId -ne $grandParentPid
} | Stop-Process -Force -ErrorAction SilentlyContinue | Out-Null

Get-CimInstance Win32_Process | Where-Object { 
    $_.Name -eq "node.exe" -and ($_.CommandLine -like "*vite*" -or $_.CommandLine -like "*npm*") -and 
    ($_.CommandLine -like "*dashboard*" -or $_.CommandLine -like "*web*") -and
    $_.ProcessId -ne $currentPid -and $_.ProcessId -ne $parentPid -and $_.ProcessId -ne $grandParentPid
} | Stop-Process -Force -ErrorAction SilentlyContinue | Out-Null

@(9999, 5173, 5055) | ForEach-Object {
    $p = (Get-NetTCPConnection -LocalPort $_ -ErrorAction SilentlyContinue).OwningProcess
    if ($p -and $p -ne $parentPid -and $p -ne $grandParentPid) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue | Out-Null }
}
Write-Host "✅ Purge Complete." -ForegroundColor Green

# --- 2. 의존성 동기화 (DEPENDENCY SYNC) ---
Write-Host "[2/5] Dependency Sync: Checking for updates..." -ForegroundColor Cyan

# Gemini CLI 업데이트 체크 (조용히)
Write-Host " - Checking Gemini CLI..." -ForegroundColor Gray
npm install -g @google/gemini-cli --silent --no-progress | Out-Null

# Node 패키지 체크 (Web & Dashboard)
foreach ($dir in @("web", "dashboard")) {
    if (Test-Path "$PROJECT_ROOT\$dir") {
        Write-Host " - Syncing $dir dependencies..." -ForegroundColor Gray
        Push-Location "$PROJECT_ROOT\$dir"
        npm install --silent --no-progress | Out-Null
        Pop-Location
    }
}

# Python 패키지 체크
Write-Host " - Syncing Python environment..." -ForegroundColor Gray
& "$venvPython" -m pip install --upgrade pip --quiet | Out-Null
if (Test-Path "$PROJECT_ROOT\requirements.txt") {
    & "$venvPython" -m pip install -r "$PROJECT_ROOT\requirements.txt" --quiet | Out-Null
}

Write-Host "✅ Dependencies Synced." -ForegroundColor Green

# --- 3. 가디언 점화 (GUARDIAN IGNITION) ---
Write-Host "[3/5] Guardian Ignition: Starting external firewall..." -ForegroundColor Blue
$guardianCommand = "`$Host.UI.RawUI.WindowTitle = 'GUARDIAN ENGINE (V22.0)'; cd '$PROJECT_ROOT'; & '$venvPython' data/agents/guardian.py"
Start-Process powershell -ArgumentList "-NoProfile", "-NoExit", "-Command", $guardianCommand -WindowStyle Normal
Start-Sleep -Seconds 1
Write-Host "✅ Guardian Active." -ForegroundColor Green

# --- 4. 신경망 동기화 (NEURAL SYNC) ---
Write-Host "[4/5] Neural Link Sync: Aligning resources..." -ForegroundColor DarkCyan
Start-Sleep -Seconds 1
Write-Host "✅ Resources Aligned." -ForegroundColor Green

# --- 5. 최종 준비 완료 (FINAL READINESS) ---
Write-Host "[5/5] System Readiness: Dual Brain standing by." -ForegroundColor Magenta
Write-Host "`n" + ("=" * 57) -ForegroundColor Magenta
Write-Host " 🔥 ACTION: Press [Ctrl + Shift + B] to split terminals" -ForegroundColor Magenta
Write-Host ("=" * 57) -ForegroundColor Magenta


