@echo off
rem ==============================================================================
rem SCRIPT: INSTALAR DEPENDENCIAS Y CONFIGURAR ENTORNO
rem ==============================================================================
rem Crea el entorno virtual 'venv' (si no existe) e instala las librerias
rem especificadas en requirements.txt (Spyne, PyMySQL, etc.).
rem ==============================================================================

title Instalar Dependencias del Proyecto

cd /d "%~dp0\.."

echo ====================================================================
echo             CONFIGURANDO ENTORNO VIRTUAL Y DEPENDENCIAS
echo ====================================================================
echo.

if not exist "venv" (
    echo Creando entorno virtual 'venv'...
    python -m venv venv
) else (
    echo El entorno virtual 'venv' ya existe.
)

echo.
echo Instalando / actualizando dependencias desde requirements.txt...
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\pip.exe install -r requirements.txt

echo.
echo ====================================================================
echo Instalacion completada exitosamente.
echo ====================================================================
pause
