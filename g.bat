@echo off
:: g.bat (V25.3.4 - Practitioner Infrastructure Restoration)
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

:: [CORE] 기동 전 모든 물리적 빗장 해제
python -X utf8 data/agents/unlock_all.py

:: PowerShell을 통해 실무자 가디언 점화
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\g.ps1"
