@echo off
title Rafael AI - Servidor API y Web UI
echo ===================================================
echo        Iniciando Entorno Web de Rafael AI
echo ===================================================

echo [1/2] Iniciando Servidor API Python en segundo plano (puerto 8000)...
start "Rafael API Server" cmd /k ".\venv\Scripts\python.exe api_server.py"

echo [2/2] Iniciando Servidor de Desarrollo Web (UI)...
cd UI
call npm.cmd run dev

pause
