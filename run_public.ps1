# Medley Lease Analysis & Management - Public URL Launcher
# This script starts the Streamlit app and creates a public ngrok tunnel

param(
    [string]$Password = "Medley2026",
    [int]$Port = 8501
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Medley Lease Analysis & Management" -ForegroundColor Cyan
Write-Host "  Public Access" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Set the app password
$env:APP_PASSWORD = $Password
Write-Host "App password set to: $Password" -ForegroundColor Yellow
Write-Host ""

# Check if ngrok is installed
$ngrokPath = Get-Command ngrok -ErrorAction SilentlyContinue
if (-not $ngrokPath) {
    Write-Host "ERROR: ngrok is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install ngrok using one of these methods:" -ForegroundColor Yellow
    Write-Host "  1. winget install ngrok.ngrok"
    Write-Host "  2. choco install ngrok"
    Write-Host "  3. Download from https://ngrok.com/download"
    Write-Host ""
    Write-Host "After installing, run: ngrok config add-authtoken YOUR_TOKEN"
    Write-Host "(Get your token at https://dashboard.ngrok.com/get-started/your-authtoken)"
    exit 1
}

# Check if ngrok is authenticated
$ngrokConfig = ngrok config check 2>&1
if ($ngrokConfig -match "error") {
    Write-Host "WARNING: ngrok may not be authenticated." -ForegroundColor Yellow
    Write-Host "Run: ngrok config add-authtoken YOUR_TOKEN" -ForegroundColor Yellow
    Write-Host ""
}

# Start Streamlit in background
Write-Host "Starting Streamlit on port $Port..." -ForegroundColor Green
$streamlitJob = Start-Job -ScriptBlock {
    param($dir, $port)
    Set-Location $dir
    streamlit run interfaces/chat_app.py --server.port $port --server.headless true
} -ArgumentList (Get-Location), $Port

# Wait for Streamlit to start
Write-Host "Waiting for Streamlit to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# Check if Streamlit started successfully
$streamlitRunning = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue
if (-not $streamlitRunning.TcpTestSucceeded) {
    Write-Host "Waiting a bit longer for Streamlit..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Starting ngrok tunnel..." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your public URL will appear below." -ForegroundColor Cyan
Write-Host "Share this URL with others to access the app." -ForegroundColor Cyan
Write-Host ""
Write-Host "Password: $Password" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Gray
Write-Host ""

# Start ngrok (this will block and show the URL)
try {
    ngrok http $Port
}
finally {
    # Cleanup
    Write-Host ""
    Write-Host "Shutting down..." -ForegroundColor Yellow
    Stop-Job $streamlitJob -ErrorAction SilentlyContinue
    Remove-Job $streamlitJob -ErrorAction SilentlyContinue
    Write-Host "Done." -ForegroundColor Green
}
