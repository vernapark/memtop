# Keep bot alive script
$ErrorActionPreference = "Continue"

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Starting Telegram Bot (24/7 Mode)" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

while ($true) {
    try {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Starting bot..." -ForegroundColor Green
        
        cd $PSScriptRoot
        python telegram_bot.py 2>&1
        
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Bot stopped. Restarting in 5 seconds..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    } catch {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Restarting in 5 seconds..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
}
