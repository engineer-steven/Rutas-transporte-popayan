# MoviPopayán - Sistema de Microservicios de Transporte Público (SOAP)

Plataforma basada en **microservicios web SOAP** (utilizando Python y Spyne) para la gestión, consulta y control operativo de rutas de transporte público en Popayán.

---

## 🏛️ Estructura Limpia del Proyecto

El proyecto está organizado de manera sencilla y modular:

```text
proyecto rutas/
├── .gitignore
├── README.md                                          # Guía general del proyecto y requisitos a desarrollar
├── requirements.txt                                   # Librerías necesarias de Python (Spyne, PyMySQL, etc.)
│
├── base_de_datos/                                     # Módulo de Base de Datos MySQL
│   ├── conexion_bd.py                                 # Configuración y función de conexión a la base de datos
│   └── esquema_bd.sql                                 # Script SQL con creación de tablas y datos iniciales
│
├── microservicios/                                    # Código de los Microservicios SOAP
│   ├── servicio_rutas/                                # Microservicio 1: Consulta y Gestión de Rutas
│   │   ├── __init__.py
│   │   └── servidor_rutas.py                          # Servidor SOAP de Rutas (Puerto 8001)
│   │
│   └── servicio_operaciones/                          # Microservicio 2: Operaciones y Tiempos
│       ├── __init__.py
│       └── servidor_operaciones.py                    # Servidor SOAP de Operaciones (Puerto 8002)
│
├── ejecutar_servidores/                               # Ejecutables para iniciar el sistema
│   └── iniciar_servidores.bat                         # Lanzador en 1 clic que abre ambos servidores
│
└── scripts/                                           # Scripts auxiliares
    └── instalar_dependencias.bat                      # Instalador automático del entorno virtual y librerías
```

---

## 📋 Guía de Implementación: Lo Que Hay Que Hacer

Cada archivo contiene su esqueleto estructurado con comentarios `# TODO` y explicaciones paso a paso de lo que debes programar:

### 1. `base_de_datos/conexion_bd.py`
- **Librería:** `pymysql`.
- **Configuración:** Establecer variables de conexión (`host`, `user`, `password`, `db='movi_popayan_db'`, `port=3306`).
- **Función:** Implementar `get_db_connection()` para abrir y retornar una conexión con cursor de tipo diccionario (`pymysql.cursors.DictCursor`).

### 2. `base_de_datos/esquema_bd.sql`
- Crear la base de datos `movi_popayan_db`.
- Definir las 4 tablas principales con sus tipos de datos y llaves primarias:
  1. `routes`: Rutas de transporte (código, empresa, origen, destino, tarifa, horario, estado).
  2. `stops`: Paraderos y puntos de referencia de cada ruta con su orden (`stop_order`).
  3. `dispatches`: Control de despachos de buses (placa, hora de salida, ruta asociada).
  4. `incidents`: Reporte de eventualidades, trancones o accidentes en ruta.
- Agregar sentencias `INSERT INTO` con datos reales de Popayán para pruebas.

### 3. `microservicios/servicio_rutas/servidor_rutas.py` (Puerto 8001)
- Definir el modelo SOAP `Route` (id, code, company, origin, destination, fare, schedule, status).
- En la clase `RoutesService(ServiceBase)`, implementar las operaciones:
  - `get_all_routes(ctx)`: Consultar y listar todas las rutas.
  - `get_route_by_id(ctx, route_id)`: Buscar una ruta específica por ID.
  - `search_routes_by_zone(ctx, zone_keyword)`: Filtrar rutas que pasen por un sector clave (ej: Campanario, Centro).
  - `add_route(ctx, ...)`: Insertar una nueva ruta en la base de datos.
- Configurar el servidor WSGI en `http://127.0.0.1:8001/?wsdl`.

### 4. `microservicios/servicio_operaciones/servidor_operaciones.py` (Puerto 8002)
- Definir los modelos SOAP: `Stop`, `Incident` y `BusTimeDifferenceResult`.
- En la clase `OperationsService(ServiceBase)`, implementar las operaciones:
  - `calculate_bus_time_difference(ctx, route_id, bus_plate_1, bus_plate_2)`: Consultar la hora de salida de dos buses en la misma ruta y calcular la diferencia en minutos.
  - `calculate_time_gap(ctx, time_1, time_2)`: Calcular minutos de diferencia entre dos cadenas horarias.
  - `get_stops_by_route(ctx, route_id)`: Devolver los paraderos ordenados por trayecto.
  - `report_incident(ctx, ...)`: Registrar una novedad vial.
  - `get_incidents_by_route(ctx, route_id)`: Listar novedades viales activas.
- Configurar el servidor WSGI en `http://127.0.0.1:8002/?wsdl`.

### 5. `ejecutar_servidores/iniciar_servidores.bat`
- Archivo por lotes que abre dos ventanas de consola simultáneas:
  - Consola 1: Ejecuta `python microservicios\servicio_rutas\servidor_rutas.py`
  - Consola 2: Ejecuta `python microservicios\servicio_operaciones\servidor_operaciones.py`

---

## 🚀 Cómo Sincronizar y Subir a GitHub

Para registrar la nueva estructura limpia y sincronizarla con tu repositorio remoto de GitHub, ejecuta en tu terminal:

```bash
# 1. Agregar todos los cambios (archivos eliminados, renombrados y nuevos)
git add -A

# 2. Confirmar los cambios con un mensaje descriptivo
git commit -m "refactor: estructurar carpetas en base_de_datos, microservicios, ejecutar_servidores y scripts con plantillas limpias"

# 3. Subir al repositorio en GitHub
git push origin main
```
*(Nota: Si tu rama principal se llama `master`, reemplaza `main` por `master`).*
