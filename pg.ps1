# pg.ps1 (Partner Guard Only Ignition)
# -----------------------------------------------------------
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$PROJECT_ROOT = $PSScriptRoot
if (-not $PROJECT_ROOT) { $PROJECT_ROOT = (Get-Location).Path }
Set-Location $PROJECT_ROOT

$guardScript = Join-Path $PROJECT_ROOT "data\agents\partner_guard.py"

Write-Host "`n[IGNITION] Waking up the Partner Guardian..." -ForegroundColor Cyan

# 가디언을 독립된 새 창에서 실행
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; `$Host.UI.RawUI.WindowTitle = 'PARTNER GUARD (V24.2)'; & python '$guardScript'; if (`$LASTEXITCODE -ne 0) { pause } }" -WindowStyle Normal

Start-Sleep -Seconds 1
Write-Host "OK: Partner Guardian is now standing watch in a new window." -ForegroundColor Green
