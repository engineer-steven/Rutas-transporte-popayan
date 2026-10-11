"""
service.py - Re-exporta app para compatibilidad retroactiva.
La aplicacion Flask ahora se ensambla con Blueprints en app.py y routes/.
"""
from app import app

__all__ = ["app"]
