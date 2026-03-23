# g.ps1 (V25.0 - Practitioner Guard Ignition)
# -----------------------------------------------------------
# 이 스크립트는 실무자용 가디언(PRISM JUDGE)을 기동합니다.
# -----------------------------------------------------------

# USB 환경 대응: 스크립트 위치 기준 절대 경로 확보
$PROJECT_ROOT = $PSScriptRoot
if (-not $PROJECT_ROOT) { $PROJECT_ROOT = (Get-Location).Path }
Set-Location $PROJECT_ROOT

Write-Host "`n[SYSTEM] Prism Judge (Practitioner Guard) Ignition..." -ForegroundColor Cyan

$guardScript = Join-Path $PROJECT_ROOT "data\agents\guardian.py"

# 새 파워쉘 창에서 실무자 가디언 실행 (시스템 파이썬 사용)
Start-Process powershell -ArgumentList "-Command", "& { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; `$Host.UI.RawUI.WindowTitle = 'PRISM JUDGE V25.0 (PRACTITIONER GUARD)'; & python '$guardScript'; if (`$LASTEXITCODE -ne 0) { pause } }" -WindowStyle Normal

# (Function registration removed as per Partner's request)
