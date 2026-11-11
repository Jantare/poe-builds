@echo off
rem Bau do PoE Builds - roda o bau.py com o Python instalado
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (py -3 bau.py %*) else (python bau.py %*)
pause
