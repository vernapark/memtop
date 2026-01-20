# Video Streaming Website Startup Script
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Video Streaming Website - Startup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Start Website Server
Write-Host "Starting Website Server..." -ForegroundColor Yellow
$webJob = Start-Job -ScriptBlock {
    param($path)
    Set-Location $path
    python -m http.server 8000
} -ArgumentList $scriptPath

# Start Telegram Bot
Write-Host "Starting Telegram Bot..." -ForegroundColor Yellow
$botJob = Start-Job -ScriptBlock {
    param($path)
    Set-Location $path
    python telegram_bot.py
} -ArgumentList $scriptPath

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  ✅ All Services Started!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Website: http://localhost:8000" -ForegroundColor Cyan
Write-Host "🔐 Admin: http://localhost:8000/parking55009hvSweJimbs5hhinbd56y" -ForegroundColor Cyan
Write-Host "🤖 Telegram Bot: Running in background" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# Keep script running
try {
    while ($true) {
        Start-Sleep -Seconds 10
        $jobs = Get-Job
        if ($jobs.Count -lt 2) {
            Write-Host "⚠️ A service stopped. Restarting..." -ForegroundColor Yellow
            Get-Job | Remove-Job -Force
            & $MyInvocation.MyCommand.Path
            break
        }
    }
} finally {
    Write-Host "Stopping services..." -ForegroundColor Yellow
    Get-Job | Stop-Job
    Get-Job | Remove-Job
    Write-Host "All services stopped." -ForegroundColor Red
}
