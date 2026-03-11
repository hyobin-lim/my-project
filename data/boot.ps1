$Host.UI.RawUI.WindowTitle = 'SUPREME COUNCIL - MASTER HUB'
cd 'D:\PROJECT-ALL\my-project'

Write-Host "--- [STAGE 1] PREPARING SERVERS ---" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoProfile", "-NoExit", "-Command", "$Host.UI.RawUI.WindowTitle = 'SERVER: DASHBOARD (9999)'; cd 'D:\PROJECT-ALL\my-project\dashboard'; npm run dev -- --port 9999" -WindowStyle Hidden
Start-Process powershell -ArgumentList "-NoProfile", "-NoExit", "-Command", "$Host.UI.RawUI.WindowTitle = 'SERVER: WEB SERVICE (5173)'; cd 'D:\PROJECT-ALL\my-project\web'; npm run dev -- --port 5173" -WindowStyle Hidden

Write-Host "--- [STAGE 2] STARTING AI AGENTS ---" -ForegroundColor Green
$agents = @("liaison_v15.py", "planner_v15.py", "watcher_v15.py", "safety_guard_v15.py", "inspector_v15.py", "terminal_nerve.py")
foreach ($agent in $agents) {
    Write-Host "Launching Agent: $agent" -ForegroundColor Cyan
    # 議곗쑉?먯? ?곕????좉꼍留앹? ?ㅼ떆媛?媛먯떆瑜??꾪빐 李쎌쓣 ?꾩?
    if ($agent -eq "liaison_v15.py" -or $agent -eq "terminal_nerve.py") {
        Start-Process -FilePath 'D:\PROJECT-ALL\my-project\.venv\Scripts\python.exe' -ArgumentList "data/agents/$agent" -WorkingDirectory 'D:\PROJECT-ALL\my-project' -WindowStyle Normal
    } else {
        Start-Process -FilePath 'D:\PROJECT-ALL\my-project\.venv\Scripts\python.exe' -ArgumentList "data/agents/$agent" -WorkingDirectory 'D:\PROJECT-ALL\my-project' -WindowStyle Hidden
    }
    Start-Sleep -Seconds 1
}

Write-Host "--- [STAGE 3] HUB ACTIVATION (FASTAPI-ASGI) ---" -ForegroundColor Green
try {
    & 'D:\PROJECT-ALL\my-project\.venv\Scripts\python.exe' "data/agents/dashboard_api.py"
} catch {
    Write-Host "
[!] CRITICAL ERROR in Nerve Hub: $($_.Exception.Message)" -ForegroundColor Red
    Pause
} finally {
    Write-Host "
[!] SHUTDOWN SIGNAL RECEIVED. Surgical cleanup in progress..." -ForegroundColor Red
    
    # 1. ?꾨줈?앺듃 愿??釉뚮씪?곗? ??쭔 ?뺣? 醫낅즺
    Get-Process | Where-Object { $_.MainWindowTitle -like '*FREEISM*' -or $_.MainWindowTitle -like '*SUPREME COUNCIL*' } | ForEach-Object {
        Write-Host "Closing Project Tab: $($_.MainWindowTitle)" -ForegroundColor Gray
        $_.CloseMainWindow() | Out-Null
    }

    # 2. ?꾨줈?앺듃 ?꾩슜 ?뚯씠???먯씠?꾪듃 ?뺣? ?ъ궡 (Surgical Kill)
    # ?쒖뒪?쒖쓽 ?ㅻⅨ ?뚯씠?ъ? 嫄대뱶由ъ? ?딄퀬, ???꾨줈?앺듃 ?대뜑 ?댁뿉???ㅽ뻾??寃껊쭔 ?≪쓬
    Write-Host "Hunting background agents in 'D:\PROJECT-ALL\my-project'..." -ForegroundColor Yellow
    Get-CimInstance Win32_Process | Where-Object { 
        $_.Name -eq "python.exe" -and ($_.CommandLine -like "*D:\PROJECT-ALL\my-project*" -or $_.ExecutablePath -like "*D:\PROJECT-ALL\my-project*")
    } | ForEach-Object {
        Write-Host "Terminating Agent PID: $($_.ProcessId)" -ForegroundColor Gray
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
    
    # 3. ?ы듃 媛뺤젣 ?댁젣 (9999: Dashboard, 5173: Web, 5055: Hub)
    @(9999, 5173, 5055) | ForEach-Object {
        $p = (Get-NetTCPConnection -LocalPort $_ -ErrorAction SilentlyContinue).OwningProcess
        if ($p) { 
            Write-Host "Releasing Port $_ (PID: $p)..." -ForegroundColor Gray
            Stop-Process -Id $p -Force -ErrorAction SilentlyContinue 
        }
    }

    Write-Host "??System fully offline. Closing this console..." -ForegroundColor Green
    Start-Sleep -Seconds 1
    exit
}
