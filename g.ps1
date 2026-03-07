# g.ps1 (Supreme Integrated Hub V8.7 - Final Victory)
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (-not $PROJECT_ROOT) { $PROJECT_ROOT = (Get-Location).Path }
Set-Location $PROJECT_ROOT
$pythonExe = Join-Path $PROJECT_ROOT ".venv\Scripts\python.exe"
$webDir = Join-Path $PROJECT_ROOT "web"
Clear-Host
Write-Host "=========================================================" -ForegroundColor Green
Write-Host "   PROJECT-ALL: HI-END TREE MODEL SYSTEM V8.7" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Green
Write-Host "[1/3] Deploying 4 Supreme Agents (Hidden)..." -ForegroundColor Cyan
$agents = @("watcher.py", "guardian.py", "inspector.py", "debater.py")
foreach ($agent in $agents) {
    $agentName = "data/agents/$agent"
    $agentPath = Join-Path $PROJECT_ROOT $agentName
    if (Test-Path $pythonExe) {
        Start-Process -FilePath $pythonExe -ArgumentList $agentPath -WorkingDirectory $PROJECT_ROOT -WindowStyle Hidden
    }
}
Write-Host "[2/3] Launching Web Dashboard (Vite)..." -ForegroundColor Cyan
if (Test-Path "$webDir\node_modules") {
    Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass", "-Command", "cd '$webDir'; npm run dev" -WorkingDirectory $webDir
}
Write-Host "[3/3] Finalizing AI Connection..." -ForegroundColor Cyan
Write-Host "`n✅ AI Ecosystem & Web Server are now ACTIVE." -ForegroundColor Green
Write-Host "---------------------------------------------------------" -ForegroundColor Green
Write-Host ">>> CONNECTING TO GEMINI CLI COMMAND CENTER..." -ForegroundColor Yellow
Write-Host "---------------------------------------------------------`n" -ForegroundColor Green
try { npx @google/gemini-cli } catch { Read-Host "Error: $($_)" }
