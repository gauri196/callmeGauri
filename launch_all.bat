@echo off
title AstraGuard 2.4 - Full Stack Launcher
echo ======================================================================
echo    ASTRAGUARD 2.4 - HYBRID RELIABILITY INTELLIGENCE PLATFORM
echo ======================================================================
echo.
echo [1/2] Starting AstraGuard FastAPI Backend Server on port 8000...
start "AstraGuard Backend (Port 8000)" cmd /k "python server.py"

timeout /t 3 /nobreak >nul

echo [2/2] Starting AstraGuard Next.js Operator Dashboard on port 3000...
cd dashboard
start "AstraGuard Dashboard (Port 3000)" cmd /k "npm run dev"
cd ..

timeout /t 5 /nobreak >nul

echo.
echo ======================================================================
echo  AstraGuard 2.4 is running!
echo    - Operator Dashboard:  http://localhost:3000
echo    - Backend API Docs:    http://127.0.0.1:8000/docs
echo    - WebSocket Stream:    ws://127.0.0.1:8000/ws/ate-stream
echo ======================================================================
echo.
start http://localhost:3000
pause
