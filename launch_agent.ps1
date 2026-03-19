param (
    [Parameter(Mandatory=$true)]
    [string]$Role
)

$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $PROJECT_ROOT

# 환경 변수에 역할을 세팅 (가디언이 식별할 수 있도록 함)
$env:FREEISM_AGENT_ROLE = $Role

if ($Role -eq "T1") {
    $Host.UI.RawUI.WindowTitle = 'T1_EXECUTOR (BUILDER)'
    Write-Host "`n[1/2] Protocol Load: Loading CORE & Manuals..." -ForegroundColor Yellow
    Start-Sleep -Seconds 1
    
    Write-Host "[2/2] Identity Enforcement: Injecting T1_EXECUTOR DNA..." -ForegroundColor Cyan
    Start-Sleep -Seconds 1
    
    # 제미나이 실행
    gemini "You are T1_EXECUTOR. Read AI_CORE/T1_EXECUTOR.md and AI_CORE/CORE_PROTOCOL.md immediately. Acknowledge your jurisdiction."
}
elseif ($Role -eq "T2") {
    $Host.UI.RawUI.WindowTitle = 'T2_COORDINATOR (AUDITOR)'
    Write-Host "`n[1/2] Protocol Load: Loading CORE & Manuals..." -ForegroundColor Yellow
    Start-Sleep -Seconds 1
    
    Write-Host "[2/2] Identity Enforcement: Injecting T2_COORDINATOR DNA..." -ForegroundColor Magenta
    Start-Sleep -Seconds 1
    
    # 제미나이 실행
    gemini "You are T2_COORDINATOR. Read AI_CORE/T2_COORDINATOR.md and AI_CORE/CORE_PROTOCOL.md immediately. Acknowledge your jurisdiction and assume gatekeeper duties."
}
else {
    Write-Host "[!] Unknown role specified: $Role" -ForegroundColor Red
    pause
}