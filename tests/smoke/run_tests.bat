@echo off
title UI Traps Analyzer — Smoke Tests
cd /d "%~dp0"
echo.
echo  Running smoke tests against Railway backend...
echo  (Close this window to cancel)
echo.
C:\Python314\python.exe run_smoke_tests.py %*
echo.
pause
