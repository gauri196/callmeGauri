# AstraGuard 2.4 - Full Stack PowerShell Launcher
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   ASTRAGUARD 2.4 - HYBRID RELIABILITY INTELLIGENCE PLATFORM" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Launching Backend FastAPI Server (Port 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python server.py"

Start-Sleep -Seconds 3

Write-Host "[2/2] Launching Next.js Operator Dashboard (Port 3000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd dashboard; npm run dev"

Start-Sleep -Seconds 4

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " AstraGuard 2.4 is running live!" -ForegroundColor Green
Write-Host "   - Operator Dashboard:  http://localhost:3000" -ForegroundColor White
Write-Host "   - Backend API Docs:    http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "   - WebSocket Stream:    ws://127.0.0.1:8000/ws/ate-stream" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Start-Process "http://localhost:3000"
