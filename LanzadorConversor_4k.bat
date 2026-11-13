@echo off
:: Forzar a la consola de Windows a usar codificación UTF-8 (Evita caracteres raros)
chcp 65001 > nul

:: Cambiar el directorio de trabajo a la ubicación exacta de este archivo .bat
cd /d "%~dp0"

:: Cambiar el título de la ventana de la consola
title Conversor Automático 4K a 1080p - Motor Modular

:: Ejecutar el script principal de Python
python conversor_principal.py

:: Pausar la pantalla al finalizar para que no se cierre la ventana automáticamente
echo.
echo ==================================================
echo   Presiona cualquier tecla para salir...
echo ==================================================
pause > nul
