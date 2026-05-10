@echo off
cd /d "%~dp0"

echo Stopping any existing Analyzer processes...

:: Kill existing backend/frontend windows by title (best effort)
taskkill /f /fi "WINDOWTITLE eq UI Traps Backend*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq UI Traps Frontend*" >nul 2>&1

:: Kill any process holding port 8000 (catches orphaned processes regardless of window title)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)

:: Kill any process holding port 5173 (Vite dev server)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173 " ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)

timeout /t 2 /nobreak >nul

echo Starting UI Traps Analyzer...

start "UI Traps Backend" cmd /k "cd backend && python app.py"

timeout /t 3 /nobreak >nul

start "UI Traps Frontend" cmd /k "cd frontend && npm run dev"

timeout /t 4 /nobreak >nul

start http://localhost:5173
