@echo off
rem ==============================================================================
rem INICIAR FRONTEND VUE + VITE (PUERTO 5174)
rem ==============================================================================
title Frontend Vue.js - MoviPopayan (Puerto 5174)
cd /d "%~dp0\..\frontend"

npm run dev
pause
