# p.ps1 (V24.1 - Prism Partner Master Ignition)
# -----------------------------------------------------------
# 이 스크립트는 기존 세션을 완전히 종료하고 파트너 가디언과 제미나이를 새롭게 기동합니다.
# -----------------------------------------------------------

$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (-not $PROJECT_ROOT) { $PROJECT_ROOT = (Get-Location).Path }
Set-Location $PROJECT_ROOT

# --- 1. 환경 정화 (Full Purge for Fresh Start) ---
Write-Host "`n[1/3] Environment Purge: Cleaning existing sessions..." -ForegroundColor Yellow

$currentPid = $PID
Get-CimInstance Win32_Process | Where-Object { 
    ($_.Name -eq "node.exe" -or $_.Name -eq "python.exe") -and 
    ($_.CommandLine -like "*$PROJECT_ROOT*" -or $_.ExecutablePath -like "*$PROJECT_ROOT*") -and
    $_.ProcessId -ne $currentPid
} | ForEach-Object {
    try { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue } catch {}
}
Write-Host "✅ Purge Complete. Starting Fresh." -ForegroundColor Green

# --- 2. 파트너 가디언 점화 (Partner Guard in PowerShell) ---
Write-Host "[2/3] Partner Guard Ignition..." -ForegroundColor Cyan

$venvPython = Join-Path $PROJECT_ROOT ".venv\Scripts\python.exe"
$guardScript = Join-Path $PROJECT_ROOT "data\agents\partner_guard.py"

# 새 파워쉘 창에서 가디언 실행 (따옴표 문제 해결)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { `$Host.UI.RawUI.WindowTitle = '🛡️ PARTNER GUARD (V24.1)'; & '$venvPython' '$guardScript'; if (`$LASTEXITCODE -ne 0) { pause } }" -WindowStyle Normal

Start-Sleep -Seconds 2
Write-Host "✅ Partner Guard is standing watch." -ForegroundColor Green

# --- 3. 제미나이 소환 (Summoning Prism Partner) ---
Write-Host "[3/3] Summoning Prism Partner..." -ForegroundColor Magenta
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray

# 제미나이 실행 (마지막 단계)
gemini
