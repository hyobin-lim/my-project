@echo off
echo [SYSTEM] Starting Intelligence Council Agents...
:: 1. 가디언 배경 실행 (이미 실행 중이면 건너뜀)
tasklist /FI "WINDOWTITLE eq GUARDIAN_AI" | find /i "python.exe" > nul
if errorlevel 1 (
    start "GUARDIAN_AI" /min .\.venv\Scripts\python data/agents/guardian.py
)

echo [SYSTEM] Entering Gemini CLI Session...
:: 2. Gemini CLI 실행
gemini
