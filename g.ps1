# g.ps1 (V24.1 - Agent Guardian Ignition)
# -----------------------------------------------------------
# 이 스크립트는 실무자용 가디언을 기동합니다.
# -----------------------------------------------------------

$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (-not $PROJECT_ROOT) { $PROJECT_ROOT = (Get-Location).Path }
Set-Location $PROJECT_ROOT

Write-Host "`n[SYSTEM] Agent Guardian Ignition..." -ForegroundColor Cyan

$venvPython = Join-Path $PROJECT_ROOT ".venv\Scripts\python.exe"
$guardScript = Join-Path $PROJECT_ROOT "data\agents\guardian.py"

# 새 파워쉘 창에서 실무자 가디언 실행
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { `$Host.UI.RawUI.WindowTitle = '🛡️ AGENT GUARDIAN (V24.1)'; & '$venvPython' '$guardScript'; if (`$LASTEXITCODE -ne 0) { pause } }" -WindowStyle Normal

# (Function registration removed as per Partner's request)
