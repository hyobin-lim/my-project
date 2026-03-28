@echo off
:: p.bat (V25.3.4 - Sovereign Infrastructure Restoration)
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

:: [CORE] 기동 전 모든 물리적 빗장 해제
python -X utf8 data/agents/prism_partner/unlock_all.py

:: PowerShell을 통해 정밀한 점화 시퀀스 실행
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\p.ps1"
