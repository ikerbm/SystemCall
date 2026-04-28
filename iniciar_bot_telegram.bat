@echo off
title Rafael Telegram Bot
echo ==============================================
echo Iniciando Sistema...
echo ==============================================

:: Cambiamos el directorio a la carpeta de este archivo .bat (SystemCall)
cd /d "%~dp0"

:: Ejecutamos el bot usando el entorno virtual
.\venv\Scripts\python.exe -m Services.Bots.telegram_rafael
echo.
echo El bot se ha detenido.
pause
