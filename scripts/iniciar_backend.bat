@echo off
rem ==============================================================================
rem INICIAR LOS 3 MICROSERVICIOS DE TRANSPORTE (PUERTOS 5001, 5002, 5003)
rem ==============================================================================
title Microservicios Backend - MoviPopayan
cd /d "%~dp0\..\backend"

if exist "..\venv\Scripts\python.exe" (
    "..\venv\Scripts\python.exe" iniciar_microservicios.py
) else (
    python iniciar_microservicios.py
)
pause

