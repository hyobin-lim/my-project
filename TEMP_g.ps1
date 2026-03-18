# g.ps1 (AI Universal Bridge V20.0 - Infrastructure Diagnostics)
# -----------------------------------------------------------
# 이 스크립트는 AI 인프라의 물리적 상태를 진단하고 클린업을 수행합니다.
# -----------------------------------------------------------

$ErrorActionPreference = "Stop"
$PROJECT_ROOT = Get-Location

Write-Host "`n[DIAGNOSTIC] Checking AI Infrastructure..." -ForegroundColor Cyan

# 1. 포트 클린업 (좀비 프로세스 제거)
try {
    $port = 5055
    $process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "[-] Found zombie process on port $port. Terminating..." -ForegroundColor Yellow
        Stop-Process -Id $process.OwningProcess -Force
    }
} catch {
    Write-Host "[!] Port cleanup skipped." -ForegroundColor Gray
}

# 2. 가상환경 확인
if (-not (Test-Path ".\.venv")) {
    Write-Host "[!] Python Virtual Environment (.venv) not found!" -ForegroundColor Red
    exit 1
}

# 3. 필수 파일 검진
$essentialFiles = @("AI_CORE\IDENTITY.md", "AI_CORE\HANDOVER.md", "data\agents\dashboard_api.py")
foreach ($file in $essentialFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "[!] Essential file missing: $file" -ForegroundColor Red
        exit 1
    }
}

Write-Host "[SUCCESS] Infrastructure is ready for DUAL-BRAIN ignition.`n" -ForegroundColor Green
exit 0
