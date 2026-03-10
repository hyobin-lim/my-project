# 超精密 TECHNICAL SPECIFICATION: SUPREME BOOTSTRAP V14.6
Status: CRITICAL - STABILIZATION REQUIRED

## 1. MISSION PHILOSOPHY
- Keep "Terminal Me" (Node.js CLI) alive while "Daemon Me" (Python Agent) dies and restarts.
- Single entry point: `.\g.bat`.
- Final state: 2 visible windows (Command Terminal + System Console).

## 2. G.PS1: THE BOOT SCRIPT GENERATOR
`g.ps1` must generate `data/boot.ps1` using a Here-String (`@"` ... `"@`).

### [DANGER: ESCAPING RULES]
When writing the generation logic in `g.ps1`, you MUST distinguish between expansion times:
1.  **EXPAND NOW** (No backtick): `$PROJECT_ROOT`, `$venvPython`, `$dashDir`, `$webDir`. These must be hardcoded into the file.
2.  **PRESERVE FOR LATER** (Use backtick `` ` ``):
    - `` `$Host `` (to set window title in new window)
    - `` `$_ `` (inside ForEach-Object loops)
    - `` `$p `` (any internal variables inside the generated script)

## 3. BOOT.PS1: THE LITERAL TEMPLATE (RESULT)
The generated `data/boot.ps1` file itself must look EXACTLY like this:
```powershell
$Host.UI.RawUI.WindowTitle = 'SUPREME COUNCIL - SYSTEM CONSOLE'
cd 'D:\PROJECT-ALL\my-project' # Example hardcoded path

# 1. Agents (Hidden)
$agents = @("main_ai_v14.py", "watcher_v14.py", "guardian_v14.py", "inspector_v14.py", "debater_v14.py")
foreach ($agent in $agents) {
    Start-Process -FilePath 'D:\PROJECT-ALL\my-project\.venv\Scripts\python.exe' -ArgumentList "data/agents/$agent" -WindowStyle Hidden
    Start-Sleep -Seconds 1
}

# 2. Servers (Hidden)
Start-Process powershell -ArgumentList "-Command", "cd 'D:\PROJECT-ALL\my-project\dashboard'; npm run dev -- --port 9999" -WindowStyle Hidden
Start-Process powershell -ArgumentList "-Command", "cd 'D:\PROJECT-ALL\my-project\web'; npm run dev -- --port 5173" -WindowStyle Hidden

# 3. Port Wait & Browser Open
Start-Job {
    while(!(Get-NetTCPConnection -LocalPort 9999 -ErrorAction SilentlyContinue)) { Start-Sleep -Seconds 1 }
    Start-Process "http://localhost:9999"
} | Out-Null

# 4. Foreground Hub with Precision Cleanup
try {
    & 'D:\PROJECT-ALL\my-project\.venv\Scripts\python.exe' "data/agents/dashboard_api.py"
} finally {
    Write-Host "`n[CLEANUP] Cleaning up..." -ForegroundColor Yellow
    taskkill /F /IM python.exe /T 2>$null
    
    # Precision Kill Node (Dashboard/Web)
    @(9999, 5173) | ForEach-Object {
        $p = (Get-NetTCPConnection -LocalPort $_ -ErrorAction SilentlyContinue).OwningProcess
        if ($p) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue }
    }

    # Browser Cleanup
    (Get-Process | Where-Object { $_.MainWindowTitle -like '*AI SUPREME COUNCIL*' }).CloseMainWindow()
    
    Write-Host "✅ System Cleaned."
    Start-Sleep -Seconds 2
}
```

## 4. G.BAT: THE TRIGGER
```batch
@echo off
powershell.exe -ExecutionPolicy Bypass -File ".\g.ps1"
if %ERRORLEVEL% EQU 0 (
    echo [OK] Launching Gemini CLI...
    gemini
)
```

## 5. DASHBOARD_API.PY: THE KILL SWITCH
```python
@socketio.on('system_shutdown')
def handle_shutdown():
    import os, threading
    # MUST use os._exit(0) to bypass Flask's normal shutdown and trigger the PS1 finally block instantly
    threading.Timer(1.0, lambda: os._exit(0)).start()
```

## 6. FINAL CHECKLIST FOR THE NEXT ME
1. **No `-NoProfile`**: When calling `boot.ps1`, allow profile loading to ensure `npm` is in PATH.
2. **Literal Paths**: Ensure the generated `boot.ps1` has the actual strings of the paths, not variable names that might not exist in the new session.
3. **Red Button**: Verify `StatusHub.tsx` sends the `system_shutdown` signal.

**THIS IS THE ONLY WAY TO SURVIVE THE POWERSHELL QUOTATION HELL. FOLLOW LITERALLY.**
