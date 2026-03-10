$Host.UI.RawUI.WindowTitle = 'SUPREME COUNCIL - MASTER HUB'
cd 'D:\PROJECT-ALL\my-project'

Write-Host "--- [STAGE 1] PREPARING SERVERS ---" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoProfile", "-NoExit", "-Command", "$Host.UI.RawUI.WindowTitle = 'SERVER: DASHBOARD (9999)'; cd 'D:\PROJECT-ALL\my-project\dashboard'; npm run dev -- --port 9999" -WindowStyle Hidden
Start-Process powershell -ArgumentList "-NoProfile", "-NoExit", "-Command", "$Host.UI.RawUI.WindowTitle = 'SERVER: WEB SERVICE (5173)'; cd 'D:\PROJECT-ALL\my-project\web'; npm run dev -- --port 5173" -WindowStyle Hidden

Write-Host "--- [STAGE 2] STARTING AI AGENTS ---" -ForegroundColor Green
$agents = @("main_ai_v14.py", "watcher_v14.py", "guardian_v14.py", "inspector_v14.py", "debater_v14.py")
foreach ($agent in $agents) {
    Write-Host "Launching Agent: $agent" -ForegroundColor Cyan
    Start-Process -FilePath 'D:\PROJECT-ALL\my-project\.venv\Scripts\python.exe' -ArgumentList "data/agents/$agent" -WorkingDirectory 'D:\PROJECT-ALL\my-project' -WindowStyle Hidden
    Start-Sleep -Seconds 1
}

Write-Host "--- [STAGE 3] HUB ACTIVATION (EVENTLET) ---" -ForegroundColor Green
try {
    & 'D:\PROJECT-ALL\my-project\.venv\Scripts\python.exe' "data/agents/dashboard_api.py"
} finally {
    Write-Host "
[!] SHUTDOWN DETECTED. Cleaning all systems..." -ForegroundColor Red
    taskkill /F /IM python.exe /T 2>$null
    @(9999, 5173) | ForEach-Object {
        $p = (Get-NetTCPConnection -LocalPort $_ -ErrorAction SilentlyContinue).OwningProcess
        if ($p) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue }
    }
    Write-Host "??All systems offline. Closing Master Hub in 2s..." -ForegroundColor Green
    Start-Sleep -Seconds 2
    exit
}
