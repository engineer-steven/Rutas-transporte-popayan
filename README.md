# MoviPopayán - Sistema de Microservicios de Transporte Público (SOAP)

Plataforma basada en **Microservicios Web SOAP 1.1** (Python + Spyne + MySQL) para la gestión de rutas de transporte urbano, analítica avanzada de viajes, control de despachos e incidencias en la ciudad de Popayán.

---

## 🏛️ Arquitectura Modular del Proyecto

El sistema adopta una arquitectura desacoplada por capas (estándar `soap ordenado`), donde cada microservicio es autónomo e independiente:

```text
proyecto rutas/
├── README.md                                # Documentación completa del proyecto
├── requirements.txt                         # Librerías Python (Spyne, PyMySQL, lxml, etc.)
│
├── base_de_datos/                           # Esquema de persistencia
│   └── esquema_bd.sql                       # DDL de tablas y datos de prueba de Popayán
│
├── microservicios/
│   ├── servicio_rutas/                      # Microservicio 1 (Puerto 8001)
│   │   ├── config.py                        # Variables de entorno y puerto 8001
│   │   ├── database.py                      # Conexión MySQL con DictCursor y Context Manager
│   │   ├── models.py                        # Modelos SOAP Spyne (ComplexModel)
│   │   ├── repository.py                    # Consultas SQL puras y acceso a datos
│   │   ├── service.py                       # CRUD + 5 Lógicas No Planas (@rpc)
│   │   └── server.py                        # Servidor WSGI ejecutable
│   │
│   └── servicio_operaciones/                # Microservicio 2 (Puerto 8002)
│       ├── config.py                        # Variables de entorno y puerto 8002
│       ├── database.py                      # Conexión MySQL con DictCursor y Context Manager
│       ├── models.py                        # Modelos SOAP Spyne (ComplexModel)
│       ├── repository.py                    # Consultas SQL puras y acceso a datos
│       ├── service.py                       # Operaciones de intervalo, paraderos e incidentes
│       └── server.py                        # Servidor WSGI ejecutable
│
└── scripts/
    └── instalar_dependencias.bat            # Script auxiliar para instalar dependencias
```

---

## 📦 Explicación de Cada Archivo dentro de los Microservicios

Cada microservicio cuenta con 6 archivos con responsabilidades estrictamente separadas:

| Archivo | Capa / Responsabilidad | ¿Por qué existe y qué hace? |
|---|---|---|
| **`config.py`** | **Configuración** | Lee las credenciales de la base de datos (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`) y el puerto (`SERVER_PORT`) desde variables de entorno con fallbacks por defecto. Evita quemar contraseñas en el código. |
| **`database.py`** | **Conexión a BD** | Abre conexiones a MySQL usando `pymysql` con `DictCursor`. Provee el context manager `get_cursor(commit=False)` para abrir, ejecutar y cerrar la conexión automáticamente, previniendo fugas de conexiones. |
| **`models.py`** | **Contrato de Datos** | Define las clases Spyne (`ComplexModel`) con tipos primitivos (`Integer`, `Unicode`, `Float`, `Boolean`). Permite que Spyne construya el contrato WSDL para que clientes como **SoapUI** reconozcan la estructura de peticiones y respuestas. |
| **`repository.py`** | **Acceso a Datos (DAO)** | Es el **único** lugar donde se escribe código SQL (`SELECT`, `INSERT`, `UPDATE`, `DELETE`). Mapea los diccionarios devueltos por MySQL a los modelos Spyne correspondientes. |
| **`service.py`** | **Lógica de Negocio** | Define la clase `ServiceBase` con todas las operaciones decoradas con `@rpc(...)` y las **lógicas no planas** (algoritmos, cálculos, simulaciones). También instancia la `Application` SOAP 1.1. |
| **`server.py`** | **Punto de Entrada** | Empaqueta la aplicación Spyne en un servidor WSGI estándar (`make_server`) y lo pone a escuchar en el puerto correspondiente. Es el archivo que se ejecuta en terminal para probar en SoapUI. |

---

## 🗄️ Base de Datos: `base_de_datos/esquema_bd.sql`

> **Nota de diseño:** La lógica de conexión reside en el archivo `database.py` de cada microservicio, por lo que la carpeta `base_de_datos/` contiene únicamente el script SQL de creación y datos de prueba.

### Tablas del Sistema:
1. **`routes`**: Información de rutas de buses (código, empresa como *Sotracauca* o *Transpubenza*, origen, destino, tarifa, horario y estado).
2. **`stops`**: Paraderos georreferenciados asociados a cada ruta con orden secuencial (`stop_order`).
3. **`dispatches`**: Despachos de vehículos con placa (`bus_plate`) y fecha/hora de salida (`departure_time`).
4. **`incidents`**: Novedades y alertas viales activas o resueltas (congestión, accidentes, desvíos).

---

## 🚌 Microservicio 1: Servicio de Rutas (Puerto 8001)

Expone operaciones CRUD básicas y **5 Lógicas No Planas** con algoritmos avanzados:

### Operaciones CRUD y Consulta:
* `get_all_routes()`: Retorna todas las rutas activas.
* `get_route_by_id(route_id)`: Consulta detallada de una ruta por ID.
* `search_routes_by_zone(zone_keyword)`: Búsqueda flexible por sector en Popayán (*Campanario*, *Centro*, *Hospital San José*).
* `add_route(...)` / `create_route(...)`: Registro de nuevas rutas.
* `update_route(...)`: Modificación de rutas existentes.
* `delete_route(route_id)`: Eliminación de ruta con borrado en cascada.

### ⭐ Las 5 Lógicas No Planas:
1. **`plan_trip(origin_keyword, destination_keyword)`**:
   * Valida la secuencia direccional de paraderos (`s1.stop_order < s2.stop_order`).
   * Calcula cantidad de paradas intermedias, tiempo estimado de viaje (~4 min por parada) y tarifa.
2. **`suggest_transfer_trip(origin_keyword, destination_keyword)`**:
   * Algoritmo de planificación multimodal con transbordo entre 2 rutas cuando no existe conexión directa.
   * Encuentra el nodo o paradero común de cambio (*Centro/Parque Caldas* o *Terminal*), calcula tarifa combinada y tiempo total con margen de espera.
3. **`calculate_route_congestion_index(route_id)`**:
   * Cruza la ruta con la tabla de incidentes activos (`incidents`).
   * Aplica ponderaciones por tipo de evento (+20 min accidente, +15 min desvío, +10 min congestión) y calcula el índice de confiabilidad (0-100%) y nivel (*NORMAL*, *MODERADO*, *ALTO*, *CRÍTICO*).
4. **`simulate_traffic_schedule(route_id, departure_hour)`**:
   * Evalúa la hora de salida respecto a las horas pico de Popayán (*06:30–08:30*, *11:45–13:45*, *17:30–19:30*).
   * Aplica factor multiplicador de tráfico del `1.45x` y calcula la hora estimada de llegada con consejos preventivos.
5. **`compare_routes_efficiency(route_id_1, route_id_2)`**:
   * Compara dos rutas evaluando densidad de paraderos, tarifa y tiempo de ciclo completo.
   * Emite un dictamen técnico recomendando cuál es superior según rapidez o economía.

---

## ⏱️ Microservicio 2: Servicio de Operaciones (Puerto 8002)

Gestiona la operativa en vía, intervalos entre despachos de buses y novedades de tránsito:
* `calculate_bus_time_difference(route_id, bus_plate_1, bus_plate_2)`: Consulta los despachos de dos vehículos en una ruta y calcula los minutos exactos de intervalo entre salidas.
* `calculate_time_gap(time_1, time_2)`: Calculadora horaria directa entre dos cadenas de tiempo.
* `get_stops_by_route(route_id)`: Lista los paraderos de una ruta ordenados por su campo `stop_order`.
* `report_incident(route_id, incident_type, description, reported_by)`: Registra un incidente vial en la ruta.
* `get_incidents_by_route(route_id)`: Consulta las novedades viales activas reportadas para una ruta.

---

## 🚀 Puesta en Marcha y Pruebas en SoapUI

### 1. Activar Entorno Virtual e Instalar Dependencias
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Importar Base de Datos en MySQL
Ejecuta el archivo `base_de_datos/esquema_bd.sql` en phpMyAdmin, MySQL Workbench o consola MySQL.

### 3. Ejecutar los Servidores

* **Terminal 1 (Rutas):**
  ```powershell
  python microservicios\servicio_rutas\server.py
  ```
  > WSDL: **`http://127.0.0.1:8001/?wsdl`**

* **Terminal 2 (Operaciones):**
  ```powershell
  python microservicios\servicio_operaciones\server.py
  ```
  > WSDL: **`http://127.0.0.1:8002/?wsdl`**

### 4. Probar en SoapUI
1. Abre **SoapUI**.
2. Selecciona **File -> New SOAP Project**.
3. En **Initial WSDL**, pega la URL del servicio que deseas probar (ej: `http://127.0.0.1:8001/?wsdl`).
4. SoapUI generará automáticamente todas las peticiones con los esquemas XML listos para enviar y probar.
