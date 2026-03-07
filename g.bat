@echo off
:: g.bat (AI Universal Bridge V8.7)
:: -----------------------------------------------------------
:: -NoProfile을 제거하여 시스템 경로(npm 등)를 정상적으로 인식하게 합니다.
:: -----------------------------------------------------------

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

:: PowerShell V8.7 통합 스크립트 실행
:: -NoProfile 옵션을 제거했습니다. (중요)
powershell.exe -ExecutionPolicy Bypass -File ".\g.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!! ERROR] AI Ecosystem failed to start with Error Code: %ERRORLEVEL%
    pause
)
