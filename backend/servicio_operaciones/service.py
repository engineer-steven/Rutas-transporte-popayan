# ==============================================================================
# ARCHIVO: backend/servicio_operaciones/service.py
# RESPONSABILIDAD: Módulo puente para compatibilidad retroactiva de importaciones en MS2.
# ==============================================================================

# Importa la instancia de la aplicación Flask creada en app.py.
from app import app

# Exporta formalmente la variable 'app'.
__all__ = ["app"]
