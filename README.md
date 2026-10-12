<<<<<<< HEAD
# EnRutate - Sistema de Microservicios de Transporte Público
=======
# EnRútate - Sistema de Microservicios de Transporte Público (SOAP)
>>>>>>> 823532235b4f7d7c6b84d50d9fa70b9678f3d37a

Plataforma basada en **Microservicios Web SOAP y REST** (Python + Spyne + Flask + MySQL) para la gestión de rutas de transporte urbano, analítica avanzada de viajes, control de despachos, telemetría de aforo y alertas en la ciudad de Popayán.

---

## 🏛️ Arquitectura Modular del Proyecto

El sistema adopta una arquitectura desacoplada por capas, donde cada microservicio es autónomo e independiente:

```text
proyecto rutas/
├── README.md                                # Documentación completa del proyecto
├── GUIA_PRUEBAS_SOAP_Y_FUNCIONES.md         # Guía de pruebas para microservicios SOAP
├── GUIA_PRUEBAS_REST_MICROSERVICIO_3.md     # Guía completa del Microservicio 3 REST (JWT + 5 Endpoints)
├── requirements.txt                         # Dependencias Python (Spyne, Flask, PyJWT, PyMySQL, etc.)
├── EnRutate_Microservicios_Entrega.zip      # Archivo comprimido listo para la entrega oficial
│
├── base_de_datos/                           # Esquema de persistencia
│   └── esquema_bd.sql                       # Tablas y datos de prueba completos con inserts
│
├── microservicios/
│   ├── servicio_rutas/                      # Microservicio 1 (SOAP - Puerto 8001)
│   │   ├── config.py, database.py, models.py, repository.py, service.py, server.py
│   │
│   ├── servicio_operaciones/                # Microservicio 2 (SOAP - Puerto 8002)
│   │   ├── config.py, database.py, models.py, repository.py, service.py, server.py
│   │
│   └── servicio_monitoreo/                  # Microservicio 3 (REST - Puerto 5003)
│       ├── .env                             # Variables de entorno y puerto 5003
│       ├── config.py                        # Configuración tipada
│       ├── database.py                      # Conexión MySQL con DictCursor
│       ├── auth.py                          # Seguridad JWT Bearer / API Key y @token_required
│       ├── repository.py                    # Acceso a datos de usuarios, calificaciones y telemetría
│       ├── service.py                       # 5 Lógicas No Lineales de alta relevancia
│       ├── rutas/                           # Endpoints REST (Flask Blueprints)
│       └── server.py                        # Servidor REST ejecutable
│
└── scripts/
    ├── instalar_dependencias.bat            # Instala librerías en venv
    ├── iniciar_servicio_monitoreo.bat       # Levanta el Microservicio 3 (Puerto 5003)
    ├── iniciar_todos_los_servicios.bat      # Levanta los 3 microservicios a la vez
    ├── probar_servicio_monitoreo.py         # Test automatizado de Login, JWT y 5 endpoints
    ├── comprimir_proyecto.bat               # Empaqueta el ZIP de entrega oficial
    └── comprimir_proyecto.py                # Script de compresión selectiva
```

---

## 📦 Explicación de Cada Archivo dentro de los Microservicios

Cada microservicio cuenta con 6 archivos con responsabilidades estrictamente separadas:

| Archivo             | Capa / Responsabilidad   | ¿Por qué existe y qué hace?                                                                                                                                                                                                                   |
| ------------------- | ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`config.py`**     | **Configuración**        | Lee las credenciales de la base de datos (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`) y el puerto (`SERVER_PORT`) desde variables de entorno con fallbacks por defecto. Evita quemar contraseñas en el código.                            |
| **`database.py`**   | **Conexión a BD**        | Abre conexiones a MySQL usando `pymysql` con `DictCursor`. Provee el context manager `get_cursor(commit=False)` para abrir, ejecutar y cerrar la conexión automáticamente, previniendo fugas de conexiones.                                   |
| **`models.py`**     | **Contrato de Datos**    | Define las clases Spyne (`ComplexModel`) con tipos primitivos (`Integer`, `Unicode`, `Float`, `Boolean`). Permite que Spyne construya el contrato WSDL para que clientes como **SoapUI** reconozcan la estructura de peticiones y respuestas. |
| **`repository.py`** | **Acceso a Datos (DAO)** | Es el **único** lugar donde se escribe código SQL (`SELECT`, `INSERT`, `UPDATE`, `DELETE`). Mapea los diccionarios devueltos por MySQL a los modelos Spyne correspondientes.                                                                  |
| **`service.py`**    | **Lógica de Negocio**    | Define la clase `ServiceBase` con todas las operaciones decoradas con `@rpc(...)` y las **lógicas no planas** (algoritmos, cálculos, simulaciones). También instancia la `Application` SOAP 1.1.                                              |
| **`server.py`**     | **Punto de Entrada**     | Empaqueta la aplicación Spyne en un servidor WSGI estándar (`make_server`) y lo pone a escuchar en el puerto correspondiente. Es el archivo que se ejecuta en terminal para probar en SoapUI.                                                 |

---

## 🗄️ Base de Datos: `enrutate_db`

El esquema y los datos iniciales se crean con `base_de_datos/esquema_bd.sql`.

> **Nota de diseño:** La lógica de conexión reside en el archivo `database.py` de cada microservicio, por lo que la carpeta `base_de_datos/` contiene únicamente el script SQL de creación y datos de prueba.

### Tablas del Sistema:
<<<<<<< HEAD

1. **`rutas`**: Información de rutas de buses (código, empresa como _Sotracauca_ o _Transpubenza_, origen, destino, tarifa, horario y estado).
2. **`paradas`**: Paraderos asociados a cada ruta con orden secuencial (`stop_order`).
3. **`despachos`**: Despachos de vehículos con placa (`bus_plate`) y fecha/hora de salida (`departure_time`).
4. **`incidentes`**: Novedades y alertas viales activas o resueltas (congestión, accidentes, desvíos).
5. **`usuarios`**: Usuarios para autenticación JWT del servicio SOAP.
6. **`usuarios_api`**: Usuarios, roles y claves API del servicio REST.
7. **`calificaciones_servicio`**: Calificaciones de calidad y satisfacción del servicio.
8. **`telemetria_buses`**: Lecturas de ocupación y velocidad de los buses.
9. **`alertas_emergencia`**: Alertas críticas de seguridad y emergencias.
=======
1. **`rutas`**: Información de rutas de buses (código, empresa como *Sotracauca* o *Transpubenza*, origen, destino, tarifa, horario y estado).
2. **`paraderos`**: Paraderos asociados a cada ruta con orden secuencial (`orden`) y punto de referencia (`referencia`).
3. **`despachos`**: Despachos de vehículos con placa (`placa_bus`) y fecha/hora de salida (`hora_salida`).
4. **`incidentes`**: Novedades y alertas viales activas o resueltas (congestión, accidentes, desvíos).
>>>>>>> 823532235b4f7d7c6b84d50d9fa70b9678f3d37a

---

## 🚌 Microservicio 1: Servicio de Rutas (Puerto 8001)

Expone operaciones CRUD básicas y **5 Lógicas No Planas** con algoritmos avanzados:

### Operaciones CRUD y Consulta:

- `get_all_routes()`: Retorna todas las rutas activas.
- `get_route_by_id(route_id)`: Consulta detallada de una ruta por ID.
- `search_routes_by_zone(zone_keyword)`: Búsqueda flexible por sector en Popayán (_Campanario_, _Centro_, _Hospital San José_).
- `add_route(...)`: Registro de nuevas rutas.
- `update_route(...)`: Modificación de rutas existentes.
- `delete_route(route_id)`: Eliminación de ruta con borrado en cascada.

### ⭐ Las 5 Lógicas No Planas:

1. **`plan_trip(origin_keyword, destination_keyword)`**:
<<<<<<< HEAD
   - Valida la secuencia direccional de paraderos (`s1.stop_order < s2.stop_order`).
   - Calcula cantidad de paradas intermedias, tiempo estimado de viaje (~4 min por parada) y tarifa.
=======
   * Valida la secuencia direccional de paraderos (`s1.orden < s2.orden`).
   * Calcula cantidad de paradas intermedias, tiempo estimado de viaje (~4 min por parada) y tarifa.
>>>>>>> 823532235b4f7d7c6b84d50d9fa70b9678f3d37a
2. **`suggest_transfer_trip(origin_keyword, destination_keyword)`**:
   - Algoritmo de planificación multimodal con transbordo entre 2 rutas cuando no existe conexión directa.
   - Encuentra el nodo o paradero común de cambio (_Centro/Parque Caldas_ o _Terminal_), calcula tarifa combinada y tiempo total con margen de espera.
3. **`calculate_route_congestion_index(route_id)`**:
<<<<<<< HEAD
   - Cruza la ruta con la tabla de incidentes activos (`incidentes`).
   - Aplica ponderaciones por tipo de evento (+20 min accidente, +15 min desvío, +10 min congestión) y calcula el índice de confiabilidad (0-100%) y nivel (_NORMAL_, _MODERADO_, _ALTO_, _CRÍTICO_).
=======
   * Cruza la ruta con la tabla de incidentes activos (`incidentes`).
   * Aplica ponderaciones por tipo de evento (+20 min accidente, +15 min desvío, +10 min congestión) y calcula el índice de confiabilidad (0-100%) y nivel (*NORMAL*, *MODERADO*, *ALTO*, *CRÍTICO*).
>>>>>>> 823532235b4f7d7c6b84d50d9fa70b9678f3d37a
4. **`simulate_traffic_schedule(route_id, departure_hour)`**:
   - Evalúa la hora de salida respecto a las horas pico de Popayán (_06:30–08:30_, _11:45–13:45_, _17:30–19:30_).
   - Aplica factor multiplicador de tráfico del `1.45x` y calcula la hora estimada de llegada con consejos preventivos.
5. **`compare_routes_efficiency(route_id_1, route_id_2)`**:
   - Compara dos rutas evaluando densidad de paraderos, tarifa y tiempo de ciclo completo.
   - Emite un dictamen técnico recomendando cuál es superior según rapidez o economía.

---

## ⏱️ Microservicio 2: Servicio de Operaciones (Puerto 8002)

Gestiona la operativa en vía, intervalos entre despachos de buses y novedades de tránsito:
<<<<<<< HEAD

- `calculate_bus_time_difference(route_id, bus_plate_1, bus_plate_2)`: Consulta los despachos de dos vehículos en una ruta y calcula los minutos exactos de intervalo entre salidas.
- `calculate_time_gap(time_1, time_2)`: Calculadora horaria directa entre dos cadenas de tiempo.
- `get_stops_by_route(route_id)`: Lista los paraderos de una ruta ordenados por su campo `stop_order`.
- `report_incident(route_id, incident_type, description, reported_by)`: Registra un incidente vial en la ruta.
- `get_incidents_by_route(route_id)`: Consulta las novedades viales activas reportadas para una ruta.
=======
* `calculate_bus_time_difference(route_id, bus_plate_1, bus_plate_2)`: Consulta los despachos de dos vehículos en una ruta y calcula los minutos exactos de intervalo entre salidas.
* `calculate_time_gap(time_1, time_2)`: Calculadora horaria directa entre dos cadenas de tiempo.
* `get_stops_by_route(route_id)`: Lista los paraderos de una ruta ordenados por su campo `orden`.
* `report_incident(route_id, incident_type, description, reported_by)`: Registra un incidente vial en la ruta.
* `get_incidents_by_route(route_id)`: Consulta las novedades viales activas reportadas para una ruta.
>>>>>>> 823532235b4f7d7c6b84d50d9fa70b9678f3d37a

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

- **Terminal 1 (Rutas):**

  ```powershell
  python microservicios\servicio_rutas\server.py
  ```

  > WSDL: **`http://127.0.0.1:8001/?wsdl`**

- **Terminal 2 (Operaciones):**
  ```powershell
  python microservicios\servicio_operaciones\server.py
  ```
  > WSDL: **`http://127.0.0.1:8002/?wsdl`**

> Si ya tenías un archivo `.env`, actualiza `DB_NAME=enrutate_db` y ejecuta de nuevo `base_de_datos/esquema_bd.sql` para crear y poblar la nueva base de datos.

### 4. Probar en SoapUI

1. Abre **SoapUI**.
2. Selecciona **File -> New SOAP Project**.
3. En **Initial WSDL**, pega la URL del servicio que deseas probar (ej: `http://127.0.0.1:8001/?wsdl`).
4. SoapUI generará automáticamente todas las peticiones con los esquemas XML listos para enviar y probar.
