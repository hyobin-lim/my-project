# g.ps1
Write-Host "`n[SYSTEM] Deploying 4 Supreme Agents (Watcher, Guardian, Inspector, Debater)..." -ForegroundColor Cyan

# 필수 파일 초기화
New-Item -Path "data/agents/plan.txt" -ItemType File -Force | Out-Null
New-Item -Path "data/agents/task.txt" -ItemType File -Force | Out-Null
New-Item -Path "data/agents/debate.txt" -ItemType File -Force | Out-Null

# 1. 4인 사령부 에이전트 배경 실행 (Hidden Window)
$agents = @("watcher.py", "guardian.py", "inspector.py", "debater.py")
foreach ($agent in $agents) {
    $procName = $agent.Split(".")[0].ToUpper() + "_AI"
    # 기존 프로세스가 있다면 종료 (중복 방지)
    Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -eq $procName } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "data/agents/$agent" -WindowStyle Hidden -Title $procName
}

Write-Host "✅ 4-Agent Supreme Council is now ACTIVE and watching you.`n" -ForegroundColor Green
Write-Host "[SYSTEM] Entering Gemini CLI Session (Main AI)...`n" -ForegroundColor Green

# 2. 메인 AI (Gemini CLI) 실행
gemini
