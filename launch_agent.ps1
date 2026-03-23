# launch_agent.ps1 (V25.0 - Prism Practitioner Ignition)
# -----------------------------------------------------------
# 이 스크립트는 새로운 실무자(Practitioner) 터미널을 점화합니다:
# 1. 가디언 등대(Prism Judge)를 찾아 핸드셰이크를 수행합니다.
# 2. 할당된 역할에 맞는 BIOS 매뉴얼 경로를 수령합니다.
# 3. 실무자에게 정체성 주입 및 초기 프로토콜 수행을 안내합니다.
# -----------------------------------------------------------

param (
    [Parameter(Mandatory=$true)]
    [ValidateSet("T1", "T2")]
    [string]$Role
)

# USB 환경 대응: 스크립트 위치 기준 절대 경로 확보
$PROJECT_ROOT = $PSScriptRoot
if (-not $PROJECT_ROOT) { $PROJECT_ROOT = (Get-Location).Path }
Set-Location $PROJECT_ROOT

Clear-Host
$color = if ($Role -eq "T1") { "Cyan" } else { "Yellow" }
Write-Host "=========================================================" -ForegroundColor $color
Write-Host "   PROJECT FREEISM - PRISM PRACTITIONER IGNITION: $Role" -ForegroundColor $color
Write-Host "=========================================================" -ForegroundColor $color

# --- 1. 가디언 등대 탐색 (Prism Judge) ---
$portFile = Join-Path $PROJECT_ROOT "data/port.txt"
if (-not (Test-Path $portFile)) {
    Write-Host "[!] Error: Prism Judge (port.txt) not found. Is Judge running?" -ForegroundColor Red
    Write-Host "    Please run '.\g.ps1' or 'g' command first." -ForegroundColor Yellow
    pause
    exit 1
}

$guardianPort = (Get-Content $portFile -Raw).Trim()
Write-Host "[1/3] Connecting to Prism Judge at Port: $guardianPort..." -ForegroundColor Gray

# --- 2. 핸드셰이크 (Handshake) ---
$handshake = @{
    role = $Role
    pid  = $PID
} | ConvertTo-Json -Compress

try {
    $socket = New-Object System.Net.Sockets.TcpClient("127.0.0.1", $guardianPort)
    $stream = $socket.GetStream()
    $writer = New-Object System.IO.StreamWriter($stream)
    $reader = New-Object System.IO.StreamReader($stream)

    $writer.WriteLine($handshake)
    $writer.Flush()

    $responseJson = $reader.ReadLine()
    $response = $responseJson | ConvertFrom-Json
    
    $socket.Close()
    
    if ($response.status -eq "APPROVED") {
        Write-Host "✅ Handshake Approved: Prism Judge synchronized." -ForegroundColor Green
        $biosPath = $response.bios_path
    } else {
        Write-Host "[!] Handshake Denied: $($response.reason)" -ForegroundColor Red
        pause
        exit 1
    }
} catch {
    Write-Host "[!] Error: Could not connect to Prism Judge. Connection Refused." -ForegroundColor Red
    pause
    exit 1
}

# --- 3. 인지적 점화 안내 ---
Write-Host "[2/3] BIOS Manual Aligned: $biosPath" -ForegroundColor DarkCyan
Write-Host "[3/3] Ready for Practitioner Interaction." -ForegroundColor Magenta

Write-Host "`n" + ("-" * 57) -ForegroundColor Magenta
Write-Host "  $Role PRISM IDENTITY INITIALIZATION REQUIRED" -ForegroundColor Magenta
Write-Host ("-" * 57) -ForegroundColor Magenta
Write-Host "`n  Please execute the following command to begin:`n" -ForegroundColor Gray
Write-Host "  python -m gemini_cli" -ForegroundColor Green
Write-Host "  (Wait for 'How can I help you?') " -ForegroundColor Gray
Write-Host "`n  Then, copy and paste your BIOS manual content or path:`n" -ForegroundColor Gray
Write-Host "  `"$biosPath`"" -ForegroundColor Green
Write-Host "`n" + ("=" * 57) -ForegroundColor Magenta

# 터미널 제목 설정 및 유지
$Host.UI.RawUI.WindowTitle = "FREEISM PRACTITIONER: $Role (PID: $PID)"
