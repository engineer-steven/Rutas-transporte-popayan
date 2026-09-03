# -*- coding: utf-8 -*-
"""
==============================================================================
MICROSERVICIO 2: OPERACIONES, INTERVALOS DE TIEMPO E INCIDENCIAS (SOAP)
==============================================================================
Punto de entrada compatible con scripts de arranque (ej. iniciar_servidores.bat).
Delega la ejecución a la arquitectura modular (server.py).
"""
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from server import main

if __name__ == "__main__":
    main()
