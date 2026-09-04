@echo off
title LifeLink AI Startup Launcher
echo ======================================================================
echo           LifeLink AI - Autonomous Emergency Healthcare Platform
echo ======================================================================
echo.

echo [1/3] Starting Agent Microservice on http://127.0.0.1:8000 ...
start "LifeLink AI Agent (Port 8000)" cmd /k "cd /d C:\Users\Aravind\Projects\SolveX\agents && C:\Users\Aravind\Projects\SolveX\agents\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/3] Starting Backend Gateway API on http://127.0.0.1:8001 ...
start "LifeLink AI Backend (Port 8001)" cmd /k "cd /d C:\Users\Aravind\Projects\SolveX && C:\Users\Aravind\Projects\SolveX\agents\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload"

echo [3/3] Starting Frontend Single Page Application on http://localhost:5173 ...
start "LifeLink AI Frontend (Port 5173)" cmd /k "cd /d C:\Users\Aravind\Projects\SolveX\fontend && npm run dev"

echo.
echo ======================================================================
echo ALL LIFELINK AI SERVICES LAUNCHED IN SEPARATE COMMAND WINDOWS:
echo   - Agent API Docs:     http://127.0.0.1:8000/docs
echo   - Backend API Docs:   http://127.0.0.1:8001/docs
echo   - Frontend Web App:   http://localhost:5173
echo ======================================================================
echo.
pause
