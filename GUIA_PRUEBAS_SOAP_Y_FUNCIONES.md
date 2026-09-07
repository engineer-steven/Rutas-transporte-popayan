# 🚌 Guía Completa de Microservicios SOAP - MoviPopayán

Este documento describe a detalle cada una de las funciones implementadas en los **dos microservicios SOAP** del sistema de transporte de Popayán, explicando:
1. **¿Qué hace y para qué sirve en la vida real?** (Contexto aplicado a la movilidad de Popayán).
2. **¿Qué datos recibe como parámetros?**
3. **Petición XML exacta para copiar y pegar en SoapUI.**
4. **Respuesta esperada del servidor.**

---

## 🧭 Índice Rápido
- [📂 Arquitectura de Archivos: ¿Para Qué Sirve Cada Archivo?](#-arquitectura-de-archivos-para-qu-sirve-cada-archivo)
  - [Estructura interna de cada microservicio (Patrón en Capas)](#-estructura-interna-de-cada-microservicio-patrn-en-capas)
  - [Archivos de soporte en la raíz del proyecto](#-archivos-de-soporte-en-la-raz-del-proyecto)
- [Microservicio 1: Rutas, Planificación de Viajes y Analítica (Puerto 8001)](#-microservicio-1-servicio_rutas-puerto-8001)
  - [1. get_all_routes](#1-get_all_routes)
  - [2. get_route_by_id](#2-get_route_by_id)
  - [3. search_routes_by_zone](#3-search_routes_by_zone)
  - [4. plan_trip (⭐ Planificador de Viaje Directo)](#4-plan_trip--planificador-de-viaje-directo)
  - [5. suggest_transfer_trip (⭐ Viaje con Transbordo)](#5-suggest_transfer_trip--planificador-con-transbordo)
  - [6. calculate_route_congestion_index (⭐ Nivel de Congestión)](#6-calculate_route_congestion_index--ndice-de-congestin)
  - [7. simulate_traffic_schedule (⭐ Simulador Hora Pico)](#7-simulate_traffic_schedule--simulador-hora-pico)
  - [8. compare_routes_efficiency (⭐ Comparador de Rutas)](#8-compare_routes_efficiency--comparador-de-eficiencia)
  - [9. add_route](#9-add_route)
  - [10. delete_route](#10-delete_route)
- [Microservicio 2: Operaciones de Campo e Incidencias (Puerto 8002)](#-microservicio-2-servicio_operaciones-puerto-8002)
  - [1. calculate_bus_time_difference](#1-calculate_bus_time_difference)
  - [2. calculate_time_gap](#2-calculate_time_gap)
  - [3. get_stops_by_route](#3-get_stops_by_route)
  - [4. report_incident](#4-report_incident)
  - [5. get_incidents_by_route](#5-get_incidents_by_route)
- [💡 Consejos para la Sustentación o Exposición](#-consejos-para-la-sustentacin-o-exposicin)

---

# 📂 Arquitectura de Archivos: ¿Para Qué Sirve Cada Archivo?

Ambos microservicios (`servicio_rutas` y `servicio_operaciones`) siguen una **Arquitectura en Capas Limpia e Idéntica**. Cada archivo tiene una única responsabilidad bien definida:

```text
proyecto rutas/
├── microservicios/
│   ├── servicio_rutas/               <- Microservicio 1 (Puerto 8001)
│   │   ├── config.py                 <- 1. Lee variables de entorno y puertos
│   │   ├── database.py               <- 2. Abre y cierra conexiones seguras a MySQL
│   │   ├── models.py                 <- 3. Define modelos y esquemas XML SOAP (Spyne)
│   │   ├── repository.py             <- 4. Hace las consultas SQL directas a MySQL
│   │   ├── service.py                <- 5. Lógica de negocio y métodos @rpc SOAP
│   │   ├── server.py                 <- 6. Archivo ejecutable que arranca el servidor WSGI
│   │   └── .env                      <- 7. Configuración local de contraseñas y puertos
│   │
│   └── servicio_operaciones/         <- Microservicio 2 (Puerto 8002)
│       ├── config.py                 <- 1. Configuración y variables de entorno
│       ├── database.py               <- 2. Conector a MySQL con context manager
│       ├── models.py                 <- 3. Modelos SOAP de incidentes y despachos
│       ├── repository.py             <- 4. Consultas SQL de paraderos, tiempos y novedades
│       ├── service.py                <- 5. Algoritmos de intervalos y métodos @rpc
│       ├── server.py                 <- 6. Ejecutable que levanta el puerto 8002
│       └── .env                      <- 7. Configuración local
│
├── base_de_datos/
│   ├── esquema_bd.sql                <- Script SQL que crea las 4 tablas y datos de prueba
│   └── conexion_bd.py                <- Conexión centralizada (entrega académica de Duver)
│
├── .vscode/settings.json             <- Configura VS Code para usar el venv automáticamente
├── .env.example                      <- Plantilla segura para GitHub (sin contraseñas)
├── .env                              <- Variables de entorno activas del proyecto
├── requirements.txt                  <- Lista de librerías instaladas (spyne, pymysql, etc.)
└── README.md                         <- Documentación general del repositorio
```

---

### 🧱 Estructura interna de cada microservicio (Patrón en Capas)

| Archivo | Capa / Rol | ¿Qué hace exactamente? | ¿Por qué es importante? |
|---|---|---|---|
| **`server.py`** | **Punto de Entrada (Lanzador)** | Es el archivo que ejecutas con `python server.py`. Crea el servidor web usando `wsgiref.simple_server` y `WsgiApplication`, publica el WSDL e imprime en consola las operaciones disponibles y la URL. | Sin él, el microservicio no puede escuchar peticiones HTTP por la red ni responder en SoapUI. |
| **`service.py`** | **Lógica de Negocio y SOAP** | Hereda de `ServiceBase` de Spyne. Contiene las funciones marcadas con `@rpc(...)` que SoapUI ve. Aquí se procesan los algoritmos de viaje, validaciones de horas pico y cálculos matemáticos. | Es el corazón funcional del microservicio; define el contrato de comunicación SOAP. |
| **`models.py`** | **Modelos de Datos SOAP (XSD)** | Define las clases que heredan de `ComplexModel` (como `Route`, `TripPlanResult`, `Stop`, `Incident`). Especifica los tipos de datos XML: `Integer`, `Unicode`, `Float`, `Boolean` y el espacio de nombres (`NAMESPACE`). | Le enseña a Spyne y a SoapUI la estructura exacta de las respuestas XML para que no haya errores de tipado. |
| **`repository.py`** | **Acceso a Datos (DAO)** | Es el único archivo que escribe código SQL (`SELECT`, `INSERT`, `UPDATE`, `DELETE`). Recibe los datos de Python, ejecuta las consultas en MySQL y convierte las filas de la base de datos en objetos modelo. | Separa la base de datos de la lógica. Si mañana cambias de base de datos, solo modificas este archivo sin romper el servicio SOAP. |
| **`database.py`** | **Gestor de Conexión a MySQL** | Abre la conexión usando `pymysql` con `DictCursor`. Implementa el decorador `@contextmanager` con la función `get_cursor(commit=False)` para abrir y cerrar conexiones de forma automática. | Evita **fugas de conexiones** (connection leaks) y bloqueos en la base de datos si ocurre un error inesperado. |
| **`config.py`** | **Configuración y Entorno** | Lee las credenciales de conexión (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT`, `SERVER_PORT`) desde el archivo `.env` o variables del sistema, con valores seguros por defecto. | Evita quemar contraseñas en el código fuente, facilitando que el proyecto funcione en cualquier computador. |
| **`.env`** | **Variables Locales** | Archivo de texto plano con los valores reales de tu máquina (por ejemplo `DB_PASSWORD=`). | Protege tus contraseñas personales para que no se suban a internet. |

---

### 🛠️ Archivos de soporte en la raíz del proyecto

* **`base_de_datos/esquema_bd.sql`**: Script en lenguaje SQL que crea la base de datos `movi_popayan_db`, sus 4 tablas (`routes`, `stops`, `dispatches`, `incidents`) y puebla la información con rutas reales de Popayán (Transpubenza, Sotracauca).
* **`base_de_datos/conexion_bd.py`**: Módulo de conexión a MySQL desarrollado para la rama de base de datos (`feature/base-de-datos`). Es el entregable asignado a Duver en el plan de trabajo.
* **`.vscode/settings.json`**: Le indica a Visual Studio Code la ruta exacta del intérprete Python dentro de la carpeta `venv/` y añade los microservicios a la ruta de búsqueda para evitar advertencias de importación falsas.
* **`.env.example`**: Plantilla de ejemplo sin contraseñas privadas. Se sube a GitHub para que cualquier profesor o compañero que descargue el repositorio sepa cómo configurar su base de datos.
* **`requirements.txt`**: Listado de paquetes de Python indispensables (`spyne`, `PyMySQL`, `cryptography`, `lxml`, `requests`, `zeep`, `python-dotenv`) para instalar el entorno con un solo comando (`pip install -r requirements.txt`).

---

# 🚍 Microservicio 1: `servicio_rutas` (Puerto 8001)

* **URL del servicio:** `http://127.0.0.1:8001/`
* **WSDL:** `http://127.0.0.1:8001/?wsdl`
* **Namespace:** `popayan.transporte.rutas`
* **Rol en la vida real:** Es el sistema central de información para el ciudadano y la Secretaría de Tránsito: administra las rutas, calcula rutas óptimas estilo Google Maps y proyecta el impacto del tráfico urbano.

---

### 1. `get_all_routes`
* **¿Qué hace en la vida real?** Es el catálogo general de transporte. Equivale a consultar en la página web de la alcaldía o en paraderos inteligentes la totalidad de rutas autorizadas que operan en Popayán con sus empresas (Sotracauca, Transpubenza, etc.), tarifas y horarios.
* **Parámetros:** Ninguno.
* **Petición en SoapUI:**
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pop="popayan.transporte.rutas">
   <soapenv:Header/>
   <soapenv:Body>
      <pop:get_all_routes/>
   </soapenv:Body>
</soapenv:Envelope>
```
* **Respuesta esperada:** Lista de objetos `Route` con todas las rutas activas (Línea 1, Línea 2, Ruta 5, Ruta 9, etc.).

---

### 2. `get_route_by_id`
* **¿Qué hace en la vida real?** Consulta la ficha técnica completa de una ruta específica cuando el usuario pulsa sobre ella en una aplicación móvil.
* **Parámetros:**
  - `route_id` (Entero): Identificador numérico de la ruta (ej: `1`).
* **Petición en SoapUI:**
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pop="popayan.transporte.rutas">
   <soapenv:Header/>
   <soapenv:Body>
      <pop:get_route_by_id>
         <pop:route_id>1</pop:route_id>
      </pop:get_route_by_id>
   </soapenv:Body>
</soapenv:Envelope>
```
* **Respuesta esperada:** Código de la ruta (`L1`), empresa (`Transpubenza`), origen (`Chirimía`), destino (`Campanario`), tarifa (`2800.0`) y horario.

---

### 3. `search_routes_by_zone`
* **¿Qué hace en la vida real?** Permite a un pasajero buscar qué buses le sirven escribiendo el nombre de su barrio o sector de interés (por ejemplo: *"Campanario"*, *"Centro"*, *"Bello Horizonte"*).
* **Parámetros:**
  - `zone_keyword` (Texto): Nombre del barrio, sector o punto de referencia.
* **Petición en SoapUI:**
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pop="popayan.transporte.rutas">
   <soapenv:Header/>
   <soapenv:Body>
      <pop:search_routes_by_zone>
         <pop:zone_keyword>Campanario</pop:zone_keyword>
      </pop:search_routes_by_zone>
   </soapenv:Body>
</soapenv:Envelope>
```
* **Respuesta esperada:** Todas las rutas cuyos paraderos, orígenes o destinos coinciden con ese sector.

---

### 4. `plan_trip` (⭐ Planificador de Viaje Directo)
* **¿Qué hace en la vida real?** Es un **motor de navegación inteligente**. El usuario indica dónde está y a dónde desea ir. El algoritmo valida la **secuencia direccional** de los paraderos (es decir, que el bus vaya en el sentido correcto y no en contravía de paradas), calcula la cantidad de estaciones intermedias, el costo y el tiempo estimado de viaje (~4 minutos por paradero en la velocidad media urbana de Popayán).
* **Parámetros:**
  - `origin_keyword`: Punto o paradero de partida (ej: `Chirimia`).
  - `destination_keyword`: Punto o paradero de llegada (ej: `Campanario`).
* **Petición en SoapUI:**
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pop="popayan.transporte.rutas">
   <soapenv:Header/>
   <soapenv:Body>
      <pop:plan_trip>
         <pop:origin_keyword>Chirimia</pop:origin_keyword>
         <pop:destination_keyword>Campanario</pop:destination_keyword>
      </pop:plan_trip>
   </soapenv:Body>
</soapenv:Envelope>
```
* **Respuesta esperada:**
  - `recommended_route_code`: Código de la mejor ruta sugerida.
  - `boarding_stop`: Paradero donde debe subirse.
  - `alighting_stop`: Paradero donde debe descender.
  - `stops_count`: Número de paraderos intermedios.
  - `estimated_minutes`: Tiempo estimado en minutos.
  - `trip_summary`: Instrucción clara en lenguaje natural.

---

### 5. `suggest_transfer_trip` (⭐ Planificador con Transbordo)
* **¿Qué hace en la vida real?** En ciudades intermedias como Popayán, no todos los barrios tienen un colectivo directo entre sí. Si vas del norte extremo al sur, este algoritmo encuentra un punto de conexión en común (ej: Parque Caldas o Centro Histórico), indicándote qué primer colectivo tomar, dónde bajarte para hacer transbordo, cuál segundo colectivo abordar, la tarifa total sumada y el tiempo total con margen de espera.
* **Parámetros:**
  - `origin_keyword`: Sector origen (ej: `Bello Horizonte`).
  - `destination_keyword`: Sector destino (ej: `Chirimia`).
* **Petición en SoapUI:**
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pop="popayan.transporte.rutas">
   <soapenv:Header/>
   <soapenv:Body>
      <pop:suggest_transfer_trip>
         <pop:origin_keyword>Bello Horizonte</pop:origin_keyword>
         <pop:destination_keyword>Chirimia</pop:destination_keyword>
      </pop:suggest_transfer_trip>
   </soapenv:Body>
</soapenv:Envelope>
```
* **Respuesta esperada:** Instrucciones divididas en Paso 1 y Paso 2, nombre de paradero de transbordo, costo de ambos pasajes y tiempo total proyectado.

---

### 6. `calculate_route_congestion_index` (⭐ Nivel de Congestión)
* **¿Qué hace en la vida real?** Es un monitor de tráfico en tiempo real. Cruza los incidentes viales activos reportados en el sistema (trancones, accidentes, desvíos) y calcula:
  1. Minutos de demora proyectados por impacto de eventos viales.
  2. Nivel de afectación: `NORMAL`, `MODERADO`, `ALTO` o `CRÍTICO`.
  3. Índice de confiabilidad de la ruta de 0% a 100%.
* **Parámetros:**
  - `route_id`: ID de la ruta a monitorear (ej: `1`).
* **Petición en SoapUI:**
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pop="popayan.transporte.rutas">
   <soapenv:Header/>
   <soapenv:Body>
      <pop:calculate_route_congestion_index>
         <pop:route_id>1</pop:route_id>
      </pop:calculate_route_congestion_index>
   </soapenv:Body>
</soapenv:Envelope>
```
* **Respuesta esperada:** Nivel de congestión, retraso en minutos y diagnóstico del estado de la vía.

---

### 7. `simulate_traffic_schedule` (⭐ Simulador Hora Pico)
* **¿Qué hace en la vida real?** Simula cómo cambia la duración del recorrido según la hora del día en Popayán. Detecta si la salida cae en las franjas pico reconocidas (06:30-08:30 mañana, 11:45-13:45 mediodía, 17:30-19:30 tarde) aplicando un factor de congestión de +45% y calcula la hora exacta estimada de llegada con consejos para el pasajero.
* **Parámetros:**
  - `route_id`: ID de la ruta (ej: `1`).
  - `departure_hour`: Hora en formato `HH:MM` (ej: `07:30` para hora pico, o `10:00` para hora valle).
* **Petición en SoapUI:**
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pop="popayan.transporte.rutas">
   <soapenv:Header/>
   <soapenv:Body>
      <pop:simulate_traffic_schedule>
         <pop:route_id>1</pop:route_id>
         <pop:departure_hour>07:30</pop:departure_hour>
      </pop:simulate_traffic_schedule>
   </soapenv:Body>
</soapenv:Envelope>
```
* **Respuesta esperada:** Booleano `is_peak_hour=true`, factor 1.45, tiempo real con retraso, hora de llegada calculada y mensaje preventivo.

---

### 8. `compare_routes_efficiency` (⭐ Comparador de Eficiencia)
* **¿Qué hace en la vida real?** Herramienta de toma de decisiones para el ciudadano y reguladores. Compara dos rutas competidoras que cubren sectores similares en tres factores clave: número de paraderos, tiempo de ciclo y precio del pasaje, emitiendo un veredicto técnico sobre cuál conviene por rapidez y cuál por economía.
* **Parámetros:**
  - `route_id_1`: ID de la primera ruta (ej: `1`).
  - `route_id_2`: ID de la segunda ruta (ej: `3`).
* **Petición en SoapUI:**
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pop="popayan.transporte.rutas">
   <soapenv:Header/>
   <soapenv:Body>
      <pop:compare_routes_efficiency>
         <pop:route_id_1>1</pop:route_id_1>
         <pop:route_id_2>3</pop:route_id_2>
      </pop:compare_routes_efficiency>
   </soapenv:Body>
</soapenv:Envelope>
```
* **Respuesta esperada:** Comparativa lado a lado con paradas, tiempos, tarifas y veredicto analítico.

---

### 9. `add_route`
* **¿Qué hace en la vida real?** Registro administrativo en MySQL de una nueva línea de transporte cuando la Secretaría de Movilidad licita o aprueba un nuevo trazado.
* **Parámetros:** Código, empresa, origen, destino, tarifa, horario.
* **Petición en SoapUI:**
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pop="popayan.transporte.rutas">
   <soapenv:Header/>
   <soapenv:Body>
      <pop:add_route>
         <pop:code>R-10</pop:code>
         <pop:company>Sotracauca</pop:company>
         <pop:origin>La Paz</pop:origin>
         <pop:destination>El Mirador</pop:destination>
         <pop:fare>2800</pop:fare>
         <pop:schedule>06:00 - 20:00</pop:schedule>
      </pop:add_route>
   </soapenv:Body>
</soapenv:Envelope>
```
* **Respuesta esperada:** `<add_routeResult>true</add_routeResult>`.

---

### 10. `delete_route`
* **¿Qué hace en la vida real?** Da de baja una ruta descontinuada o suspendida.
* **Parámetros:** `route_id` (Entero).
* **Petición en SoapUI:**
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pop="popayan.transporte.rutas">
   <soapenv:Header/>
   <soapenv:Body>
      <pop:delete_route>
         <pop:route_id>99</pop:route_id>
      </pop:delete_route>
   </soapenv:Body>
</soapenv:Envelope>
```

---
---

# ⏱️ Microservicio 2: `servicio_operaciones` (Puerto 8002)

* **URL del servicio:** `http://127.0.0.1:8002/`
* **WSDL:** `http://127.0.0.1:8002/?wsdl`
* **Namespace:** `popayan.transporte.operaciones`
* **Rol en la vida real:** Es la central de despacho y control de campo. Controla frecuencias de salida, supervisa retrasos entre colectivos, lista paraderos de cada recorrido y recibe reportes viales en caliente.

---

### 1. `calculate_bus_time_difference`
* **¿Qué hace en la vida real?** **Control de intervalo de frecuencias.** El despachador o inspector en la terminal de buses debe verificar el tiempo de separación entre dos colectivos consecutivos de la misma ruta. Si salieron con menos de 5 minutos de diferencia van a competir por pasajeros (guerra del centavo), y si tienen más de 20 minutos la gente espera demasiado en las paradas.
* **Parámetros:**
  - `route_id`: ID de la ruta (ej: `1`).
  - `bus_plate_1`: Placa del primer bus (ej: `TPK-102`).
  - `bus_plate_2`: Placa del segundo bus (ej: `TPK-102`).
* **Petición en SoapUI:**
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pop="popayan.transporte.operaciones">
   <soapenv:Header/>
   <soapenv:Body>
      <pop:calculate_bus_time_difference>
         <pop:route_id>1</pop:route_id>
         <pop:bus_plate_1>TPK-102</pop:bus_plate_1>
         <pop:bus_plate_2>TPK-102</pop:bus_plate_2>
      </pop:calculate_bus_time_difference>
   </soapenv:Body>
</soapenv:Envelope>
```
* **Respuesta esperada:** Objeto con hora de salida 1 (`06:30:00`), hora de salida 2, diferencia en minutos y mensaje explicativo del estado de frecuencia.

---

### 2. `calculate_time_gap`
* **¿Qué hace en la vida real?** Calculadora utilitaria horaria sin acoplamiento a base de datos. Se usa en dos escenarios:
  1. **Control de planilla del conductor:** Compara la hora en que el bus pasó por un punto de control (`07:15:00`) versus su hora oficial programada (`07:00:00`) para saber cuántos minutos de retraso o adelanto acumula.
  2. **Planificación de frecuencias en oficina:** Los directivos de la empresa calculan intervalos teóricos antes de mandar buses a la calle.
* **Parámetros:**
  - `time_1`: Primera hora (ej: `06:30:00`).
  - `time_2`: Segunda hora (ej: `07:15:00`).
* **Petición en SoapUI:**
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pop="popayan.transporte.operaciones">
   <soapenv:Header/>
   <soapenv:Body>
      <pop:calculate_time_gap>
         <pop:time_1>06:30:00</pop:time_1>
         <pop:time_2>07:15:00</pop:time_2>
      </pop:calculate_time_gap>
   </soapenv:Body>
</soapenv:Envelope>
```
* **Respuesta esperada:** `<calculate_time_gapResult>45</calculate_time_gapResult>`.

---

### 3. `get_stops_by_route`
* **¿Qué hace en la vida real?** Muestra la **hoja de ruta secuencial de paraderos**. Permite al conductor o al usuario saber exactamente en qué orden pasa el bus y cuáles son los puntos de referencia cercanos (ej: *Frente al Campanario*, *Glorieta de la Chirimía*).
* **Parámetros:**
  - `route_id`: ID de la ruta (ej: `1`).
* **Petición en SoapUI:**
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pop="popayan.transporte.operaciones">
   <soapenv:Header/>
   <soapenv:Body>
      <pop:get_stops_by_route>
         <pop:route_id>1</pop:route_id>
      </pop:get_stops_by_route>
   </soapenv:Body>
</soapenv:Envelope>
```
* **Respuesta esperada:** Lista de paraderos ordenados por `stop_order`: Chirimía (1), Centro Histórico / Parque Caldas (2), Centro Comercial Campanario (3).

---

### 4. `report_incident`
* **¿Qué hace en la vida real?** **Reporte de novedades viales en caliente.** Cuando un conductor se topa con una manifestación, un choque o un derrumbe en Popayán, este servicio registra la alerta para que la central tome medidas y desvíe los demás vehículos.
* **Parámetros:**
  - `route_id`: Ruta afectada (ej: `1`).
  - `incident_type`: Tipo de incidente (`CONGESTION`, `ACCIDENTE`, `DESVIO`).
  - `description`: Detalle de lo sucedido.
  - `reported_by`: Quién envía la novedad (`Conductor`, `Inspector`, `Pasajero`).
* **Petición en SoapUI:**
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pop="popayan.transporte.operaciones">
   <soapenv:Header/>
   <soapenv:Body>
      <pop:report_incident>
         <pop:route_id>1</pop:route_id>
         <pop:incident_type>CONGESTION</pop:incident_type>
         <pop:description>Trafico lento cerca a la glorieta por obras publicas</pop:description>
         <pop:reported_by>Conductor 12</pop:reported_by>
      </pop:report_incident>
   </soapenv:Body>
</soapenv:Envelope>
```
* **Respuesta esperada:** `<report_incidentResult>true</report_incidentResult>`.

---

### 5. `get_incidents_by_route`
* **¿Qué hace en la vida real?** **Tablero de alertas activas.** Consulta todas las novedades no resueltas de una ruta para mostrarlas en pantallas informativas de paraderos o en la app del ciudadano antes de subirse al bus.
* **Parámetros:**
  - `route_id`: ID de la ruta a consultar (ej: `1`).
* **Petición en SoapUI:**
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pop="popayan.transporte.operaciones">
   <soapenv:Header/>
   <soapenv:Body>
      <pop:get_incidents_by_route>
         <pop:route_id>1</pop:route_id>
      </pop:get_incidents_by_route>
   </soapenv:Body>
</soapenv:Envelope>
```
* **Respuesta esperada:** Lista de incidentes con su descripción, fecha de reporte y estado `ACTIVO`.

---

# 💡 Consejos para la Sustentación o Exposición

1. **Arquitectura SOA:**
   - Destaca que el sistema cumple con **Arquitectura Orientada a Servicios (SOA)** con separación de responsabilidades:
     - **Microservicio 1 (Puerto 8001):** Capa de Rutas, Navegación y Analítica de Viajes.
     - **Microservicio 2 (Puerto 8002):** Capa Operativa, Tiempos de Despacho e Incidencias en Ruta.
2. **Lógica No Plana (Valor Agregado):**
   - No son solo operaciones CRUD simples. Explica que el proyecto incluye algoritmos avanzados como `plan_trip` (valida secuencia direccional de paraderos), `suggest_transfer_trip` (intersección entre rutas con transbordo) y `simulate_traffic_schedule` (impacto real de hora pico en Popayán).
3. **Validación en SoapUI:**
   - Muestra cómo los esquemas XML (`xsd`) garantizan tipado estricto (`Integer`, `Unicode`, `Float`, `Boolean`, `ComplexModel`) y evitan errores de datos antes de llegar a la base de datos.
