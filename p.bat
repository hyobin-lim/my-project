@echo off
:: p.bat (Wrapper for p.ps1 - VS Code & Terminal Unified)
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

:: PowerShell을 통해 정밀한 점화 시퀀스 실행
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\p.ps1"
