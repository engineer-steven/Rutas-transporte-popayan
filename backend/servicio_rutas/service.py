# ==============================================================================
# ARCHIVO: backend/servicio_rutas/service.py
# RESPONSABILIDAD: Módulo puente para compatibilidad retroactiva de importaciones.
# NOTA: En la arquitectura REST, la lógica se modularizó en Blueprints (routes/).
# ==============================================================================

# Importa la instancia principal de la aplicación Flask configurada en app.py.
from app import app

# Define explícitamente qué símbolos se exportan cuando se usa 'from service import *'.
__all__ = ["app"]
