@echo off
python -X utf8 data/agents/unlock_all.py

:: r.bat (V24.1 - Phoenix Practitioner Reboot)
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo [REBOOT] Purging Practitioner Instances (Protecting Guardians)...

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
    Write-Host ' * This will launch the FRESH DUAL-BRAIN terminals.' -ForegroundColor Gray; ^
    Write-Host ' * Agents will reconnect to the existing Guardian.' -ForegroundColor Gray; ^
    Write-Host '===========================================================' -ForegroundColor Cyan; ^
}"

pause
