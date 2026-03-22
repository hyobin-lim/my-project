# p.ps1 (V24.2 - Prism Partner Ultra-Stability Ignition)
# -----------------------------------------------------------
# 이 스크립트는 인코딩 문제를 해결하고 가디언 세션을 안정적으로 기동합니다.
# -----------------------------------------------------------

# --- 0. 인코딩 및 환경 설정 ---
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# USB 환경 대응: 스크립트 위치 기준 절대 경로 확보
$PROJECT_ROOT = $PSScriptRoot
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
Write-Host "OK: Purge Complete. Starting Fresh." -ForegroundColor Green

# --- 2. 파트너 가디언 점화 (Partner Guard using System Python) ---
Write-Host "[2/3] Partner Guard Ignition..." -ForegroundColor Cyan

$guardScript = Join-Path $PROJECT_ROOT "data\agents\partner_guard.py"

# 시스템 PATH의 파이썬을 직접 호출 (USB .venv 경로 문제 해결)
Start-Process powershell -ArgumentList "-Command", "& { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; `$Host.UI.RawUI.WindowTitle = 'PARTNER GUARD (V24.2)'; & python '$guardScript'; if (`$LASTEXITCODE -ne 0) { pause } }" -WindowStyle Normal

Start-Sleep -Seconds 2
Write-Host "OK: Partner Guard is standing watch." -ForegroundColor Green

# --- 3. 제미나이 소환 (Summoning Prism Partner) ---
Write-Host "[3/3] Summoning Prism Partner..." -ForegroundColor Magenta
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray

# 제미나이 실행
gemini
