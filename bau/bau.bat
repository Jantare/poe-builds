@echo off
rem Bau do PoE Builds - valor do bau em Chaos e Divine
chcp 65001 >nul
title Bau do PoE Builds
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (py -3 bau.py %*) else (python bau.py %*)
echo.
pause
