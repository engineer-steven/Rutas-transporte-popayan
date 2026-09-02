@echo off
rem ==============================================================================
rem INICIAR SERVIDORES - MICROSERVICIOS SOAP (POPAYÁN)
rem ==============================================================================
rem Este archivo batch inicia los servidores de los microservicios en dos consolas
rem independientes de Windows:
rem   - Microservicio 1: microservicios\servicio_rutas\servidor_rutas.py (Puerto 8001)
rem   - Microservicio 2: microservicios\servicio_operaciones\servidor_operaciones.py (Puerto 8002)
rem ==============================================================================

title Iniciar Servidores de Transporte Popayan

echo ====================================================================
echo             INICIANDO SERVIDORES DE MICROSERVICIOS
echo ====================================================================
echo.

cd /d "%~dp0\.."

set PYTHON_EXEC=python
if exist "venv\Scripts\python.exe" (
    set PYTHON_EXEC=venv\Scripts\python.exe
    echo Entorno virtual detectado: venv
) else (
    echo Usando Python del sistema
)

echo.
echo [1/2] Iniciando Servidor de Rutas (Puerto 8001)...
start "Servidor de Rutas - Puerto 8001" cmd /k "%PYTHON_EXEC% microservicios\servicio_rutas\servidor_rutas.py"

echo [2/2] Iniciando Servidor de Operaciones (Puerto 8002)...
start "Servidor de Operaciones - Puerto 8002" cmd /k "%PYTHON_EXEC% microservicios\servicio_operaciones\servidor_operaciones.py"

echo.
echo ====================================================================
echo   Servidores en ejecucion:
echo   - Rutas WSDL:       http://127.0.0.1:8001/?wsdl
echo   - Operaciones WSDL: http://127.0.0.1:8002/?wsdl
echo ====================================================================
echo Mantenga ambas ventanas abiertas mientras los servidores esten en uso.
echo.
pause
