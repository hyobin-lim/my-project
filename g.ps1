# g.ps1 (V24.1 - Agent Guardian Ignition)
# -----------------------------------------------------------
# 이 스크립트는 실무자용 가디언을 기동합니다.
# -----------------------------------------------------------

# USB 환경 대응: 스크립트 위치 기준 절대 경로 확보
$PROJECT_ROOT = $PSScriptRoot
if (-not $PROJECT_ROOT) { $PROJECT_ROOT = (Get-Location).Path }
Set-Location $PROJECT_ROOT

Write-Host "`n[SYSTEM] Agent Guardian Ignition..." -ForegroundColor Cyan

$guardScript = Join-Path $PROJECT_ROOT "data\agents\guardian.py"

# 새 파워쉘 창에서 실무자 가디언 실행 (시스템 파이썬 사용)
Start-Process powershell -ArgumentList "-Command", "& { `$Host.UI.RawUI.WindowTitle = '🛡️ AGENT GUARDIAN (V24.2)'; & python '$guardScript'; if (`$LASTEXITCODE -ne 0) { pause } }" -WindowStyle Normal

# (Function registration removed as per Partner's request)
