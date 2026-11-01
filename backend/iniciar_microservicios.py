# ==============================================================================
# ARCHIVO: backend/iniciar_microservicios.py
# RESPONSABILIDAD: Levantar los 3 microservicios simultáneamente (Puertos 5001, 5002 y 5003).
# ==============================================================================

import os
import sys
import subprocess
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXE = sys.executable

SERVICIOS = [
    {
        "nombre": "MS1: Rutas y Planificador",
        "puerto": 5001,
        "dir": os.path.join(CURRENT_DIR, "servicio_rutas"),
        "script": "server.py"
    },
    {
        "nombre": "MS2: Operaciones en Vía",
        "puerto": 5002,
        "dir": os.path.join(CURRENT_DIR, "servicio_operaciones"),
        "script": "server.py"
    },
    {
        "nombre": "MS3: Monitoreo, Despacho y Auth",
        "puerto": 5003,
        "dir": os.path.join(CURRENT_DIR, "servicio_monitoreo"),
        "script": "server.py"
    }
]


def main():
    print("=" * 76)
    print("  INICIANDO LOS 3 MICROSERVICIOS DE TRANSPORTE POPAYÁN")
    print("=" * 76)

    procesos = []
    try:
        for s in SERVICIOS:
            print(f"-> Levantando {s['nombre']} en puerto {s['puerto']}...")
            script_path = os.path.join(s["dir"], s["script"])
            proc = subprocess.Popen(
                [PYTHON_EXE, script_path],
                cwd=s["dir"]
            )
            procesos.append(proc)
            time.sleep(0.5)

        print("\n" + "=" * 76)
        print("  LOS 3 MICROSERVICIOS ESTÁN CORRIENDO EXITOSAMENTE:")
        print("  * Microservicio 1 (Rutas):       http://127.0.0.1:5001")
        print("  * Microservicio 2 (Operaciones): http://127.0.0.1:5002")
        print("  * Microservicio 3 (Monitoreo):   http://127.0.0.1:5003")
        print("  * Frontend Vue:                  http://localhost:5174")
        print("  Presione Ctrl + C para detener todos los microservicios.")
        print("=" * 76 + "\n")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nDeteniendo todos los microservicios...")
        for proc in procesos:
            try:
                proc.terminate()
            except Exception:
                pass
        print("Servicios detenidos.")


if __name__ == "__main__":
    main()

