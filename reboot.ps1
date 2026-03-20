# reboot.ps1 (V24.2 - Practitioner Pure Reset)
# -----------------------------------------------------------
# 이 스크립트는 실무자 전용 정화 도구입니다.
# 실무자 가디언(g)만 남기고 나머지 T1, T2 좀비 프로세스를 사살합니다.
# -----------------------------------------------------------

$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (-not $PROJECT_ROOT) { $PROJECT_ROOT = (Get-Location).Path }
Set-Location $PROJECT_ROOT

Clear-Host
Write-Host "=========================================================" -ForegroundColor Red
Write-Host "   PROJECT FREEISM - PRACTITIONER RESET (PHOENIX)" -ForegroundColor Red
Write-Host "=========================================================" -ForegroundColor Red

# --- 1. 실무자 가디언(g) 식별 ---
$guardianPidFile = Join-Path $PROJECT_ROOT "data\guardian.pid"
$protectedPids = @($PID) # 현재 파워쉘 세션 보호
if (Test-Path $guardianPidFile) { 
    $protectedPids += Get-Content $guardianPidFile -Raw 
    Write-Host "[1/2] Identifying Practitioner Guardian (g): PROTECTED" -ForegroundColor Gray
} else {
    Write-Host "[1/2] Practitioner Guardian (g) not found. Proceeding with full purge." -ForegroundColor Yellow
}

# --- 2. 실무자(T1, T2) 및 좀비 프로세스 정밀 사살 ---
Write-Host "[2/2] Surgical Purge: Cleaning Practitioner World..." -ForegroundColor Yellow

Get-CimInstance Win32_Process | Where-Object { 
    ($_.Name -eq "node.exe" -or $_.Name -eq "python.exe") -and 
    ($_.CommandLine -like "*$PROJECT_ROOT*" -or $_.ExecutablePath -like "*$PROJECT_ROOT*")
} | ForEach-Object {
    $targetPid = $_.ProcessId
    if ($protectedPids -notcontains $targetPid) {
        try { 
            Stop-Process -Id $targetPid -Force -ErrorAction SilentlyContinue 
            Write-Host " - Terminated: $($_.Name) (PID: $targetPid)" -ForegroundColor DarkGray
        } catch {}
    }
}

Write-Host "✅ Reset Complete. Practitioner Guardian (g) is still standing." -ForegroundColor Green
Write-Host "`n 🔥 NEXT: Press [Ctrl + Shift + B] to re-ignite T1/T2 agents." -ForegroundColor Magenta
Write-Host ("=" * 57) -ForegroundColor Magenta
