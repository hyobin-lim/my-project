@echo off
python -X utf8 data/agents/unlock_all.py

:: g.bat (AI Universal Bridge V20.5 - Elite Guide)
:: -----------------------------------------------------------
:: 이 배치 파일은 초기 환경 진단 및 2분할 터미널 기동을 안내합니다.
:: -----------------------------------------------------------

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

:: PowerShell 진단 스크립트 실행 (역할 없이 일반 진단)
powershell.exe -ExecutionPolicy Bypass -File ".\g.ps1"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [READY] Infrastructure is stable.
    echo.
    echo ===========================================================
    echo    🔥 ACTION REQUIRED: Press [Ctrl + Shift + B]
    echo ===========================================================
    echo    * This will launch the DUAL-BRAIN COMMAND CENTER.
    echo    * LEFT:  Executor (T1)
    echo    * RIGHT: Coordinator (T2)
    echo ===========================================================
    echo.
    pause
) else (
    echo.
    echo [!! ERROR] AI Infrastructure failed to start with Error Code: %ERRORLEVEL%
    pause
)
