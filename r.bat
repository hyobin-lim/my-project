@echo off
:: r.bat (V25.3.4 - Practitioner Full Purge)
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

:: [CORE] 기동 전 모든 물리적 빗장 해제
python -X utf8 data/agents/unlock_all.py

echo [REBOOT] Purging Practitioner Instances (T1/T2)...

:: PowerShell을 사용하여 정밀 정화 및 안내 수행
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& { ^
    $root = '%PROJECT_ROOT%'.TrimEnd('\'); ^
    $protectedPids = @(); ^
    if (Test-Path 'data\partner_guard.pid') { $protectedPids += (Get-Content 'data\partner_guard.pid' -Raw).Trim() } ^
    if (Test-Path 'data\guardian.pid') { $protectedPids += (Get-Content 'data\guardian.pid' -Raw).Trim() } ^
    $protectedPids += $PID; ^
    Get-CimInstance Win32_Process | Where-Object { ^
        ($_.Name -eq 'node.exe' -or $_.Name -eq 'python.exe') -and ^
        ($_.CommandLine -like \"*$root*\" -or $_.ExecutablePath -like \"*$root*\") -and ^
        $protectedPids -notcontains [string]$_.ProcessId ^
    } | ForEach-Object { try { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue } catch {} }; ^
    Write-Host 'OK: Practitioner Purge Complete. Guardians remain active.' -ForegroundColor Green; ^
    Write-Host '===========================================================' -ForegroundColor Cyan; ^
    Write-Host '   🔥 ACTION REQUIRED: Press [Ctrl + Shift + B]' -ForegroundColor Cyan; ^
    Write-Host '===========================================================' -ForegroundColor Cyan; ^
    Write-Host ' * This will launch the FRESH PRISM PRACTITIONER terminals.' -ForegroundColor Gray; ^
    Write-Host ' * Agents will reconnect to the existing Prism Judge.' -ForegroundColor Gray; ^
    Write-Host '===========================================================' -ForegroundColor Cyan; ^
}"
pause
