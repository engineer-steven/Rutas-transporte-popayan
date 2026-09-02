# 👥 Asignación de Tareas por Ramas - MoviPopayán

Este documento describe la división del trabajo del proyecto en **4 ramas independientes** para que cada integrante del equipo trabaje en su propio módulo sin generar conflictos de código.

---

## 🌳 Resumen de Ramas y Responsabilidades

| Rama | Módulo / Tarea | Archivos Asignados | Responsable |
|---|---|---|---|
| **`feature/base-de-datos`** | Base de Datos MySQL y Conexión | `base_de_datos/conexion_bd.py`<br>`base_de_datos/esquema_bd.sql` | *Duver* |
| **`feature/microservicio-rutas`** | Microservicio SOAP 1 (Puerto 8001) | `microservicios/servicio_rutas/servidor_rutas.py` | *Steven* |
| **`feature/microservicio-operaciones`** | Microservicio SOAP 2 (Puerto 8002) | `microservicios/servicio_operaciones/servidor_operaciones.py` | *Jefferson* |
| **`feature/despliegue-de-servidores`** | Lanzador, Entorno y Puesta en Marcha | `ejecutar_servidores/iniciar_servidores.bat`<br>`scripts/instalar_dependencias.bat`<br>`requirements.txt` | *Responsable de Despliegue* |

---

## 📌 Detalle de Tareas por Cada Rama

### 1️⃣ Rama: `feature/base-de-datos` *(Duver)*
> **Objetivo:** Diseñar la base de datos relacional MySQL y el módulo de conexión centralizado.

**Tareas a desarrollar:**
1. En `base_de_datos/esquema_bd.sql`:
   - Crear la base de datos `movi_popayan_db`.
   - Definir las 4 tablas con sus tipos de datos, llaves primarias y foráneas:
     - `routes`: Información general de rutas (código, empresa, origen, destino, tarifa, horario, estado).
     - `stops`: Paraderos ordenados de cada ruta (`stop_order`, punto de referencia).
     - `dispatches`: Despachos de buses con placa y hora de salida.
     - `incidents`: Reportes de eventos en ruta (congestión, accidentes, etc.).
   - Insertar datos iniciales de prueba representativos de Popayán (ej: Sotracauca, Transpubenza).
2. En `base_de_datos/conexion_bd.py`:
   - Configurar los parámetros de conexión a MySQL.
   - Implementar la función `get_db_connection()` utilizando la librería `pymysql` con `DictCursor`.

---

### 2️⃣ Rama: `feature/microservicio-rutas` *(Steven)*
> **Objetivo:** Implementar la lógica del Microservicio SOAP para la consulta y registro de rutas en Popayán (Puerto 8001).

**Tareas a desarrollar:**
En `microservicios/servicio_rutas/servidor_rutas.py`:
1. Definir el modelo complejo SOAP `Route(ComplexModel)`.
2. Implementar los 5 métodos dentro de la clase `RoutesService(ServiceBase)`:
   - `get_all_routes(ctx)`: Consultar y listar todas las rutas activas.
   - `get_route_by_id(ctx, route_id)`: Buscar y retornar el detalle de una ruta por su ID.
   - `search_routes_by_zone(ctx, zone_keyword)`: Filtrar rutas que pasen por una zona clave (ej: Campanario, Centro).
   - `add_route(ctx, code, company, origin, destination, fare, schedule)`: Registrar una nueva ruta en MySQL.
   - `plan_trip(ctx, origin_keyword, destination_keyword)`: **[Lógica No Plana]** Planificador inteligente de viajes entre 2 puntos validando la secuencia y orden de los paraderos (`stop_order`), calculando cantidad de paradas, tarifa y tiempo estimado.
3. Configurar la aplicación WSGI con Spyne y levantar el servidor en `http://127.0.0.1:8001/?wsdl`.

---

### 3️⃣ Rama: `feature/microservicio-operaciones` *(Jefferson)*
> **Objetivo:** Implementar la lógica operativa: intervalos de tiempo entre buses, paraderos e incidencias viales (Puerto 8002).

**Tareas a desarrollar:**
En `microservicios/servicio_operaciones/servidor_operaciones.py`:
1. Definir los modelos SOAP: `Stop`, `Incident` y `BusTimeDifferenceResult`.
2. Implementar los 5 métodos en `OperationsService(ServiceBase)`:
   - `calculate_bus_time_difference(ctx, route_id, bus_plate_1, bus_plate_2)`: Consultar la hora de salida de dos buses de una misma ruta y calcular los minutos de diferencia entre ambos despachos.
   - `calculate_time_gap(ctx, time_1, time_2)`: Calculadora horaria directa que recibe dos horas en texto y retorna la diferencia en minutos.
   - `get_stops_by_route(ctx, route_id)`: Consultar los paraderos ordenados por trayecto.
   - `report_incident(ctx, route_id, incident_type, description, reported_by)`: Registrar un reporte o alerta vial.
   - `get_incidents_by_route(ctx, route_id)`: Consultar alertas activas en una ruta.
3. Configurar el servidor WSGI en `http://127.0.0.1:8002/?wsdl`.

---

### 4️⃣ Rama: `feature/despliegue-de-servidores`
> **Objetivo:** Asegurar la puesta en marcha del proyecto, ejecución de servidores y gestión del entorno.

**Tareas a desarrollar:**
1. En `ejecutar_servidores/iniciar_servidores.bat`:
   - Asegurar que al ejecutar el archivo con doble clic se abran dos ventanas independientes de consola arrancando ambos microservicios (`servidor_rutas.py` y `servidor_operaciones.py`) sin errores.
2. En `scripts/instalar_dependencias.bat`:
   - Garantizar que cree el entorno virtual `venv` (si no existe) e instale las dependencias de `requirements.txt`.
3. En `requirements.txt`:
   - Verificar y mantener las versiones compatibles de `spyne`, `pymysql`, `requests`, `lxml`.
4. Pruebas de levantamiento:
   - Validar que ambos servicios respondan correctamente a sus respectivos WSDL en el navegador o cliente SOAP.

---

## 🛠️ Comandos Git para Crear y Subir las Ramas

Ejecuta estos comandos en tu terminal para crear las 4 ramas localmente y subirlas a GitHub:

```bash
# 1. Crear las 4 ramas basadas en la rama actual (main)
git branch feature/base-de-datos
git branch feature/microservicio-rutas
git branch feature/microservicio-operaciones
git branch feature/despliegue-de-servidores

# 2. Subir todas las ramas a GitHub
git push -u origin feature/base-de-datos
git push -u origin feature/microservicio-rutas
git push -u origin feature/microservicio-operaciones
git push -u origin feature/despliegue-de-servidores
```

---

## 👨‍💻 ¿Cómo Trabaja Cada Integrante?

Cada compañero debe colocarse en su rama asignada antes de programar:

```bash
# Para Duver (Base de Datos):
git checkout feature/base-de-datos

# Para Steven (Servicio de Rutas):
git checkout feature/microservicio-rutas

# Para Jefferson (Servicio de Operaciones):
git checkout feature/microservicio-operaciones

# Para el Encargado de Despliegue de Servidores:
git checkout feature/despliegue-de-servidores
```

Cuando terminen sus cambios, cada uno hace:
```bash
git add -A
git commit -m "feat: implementar módulo asignado"
git push origin <nombre-de-su-rama>
```
Luego se hace un **Pull Request (PR)** en GitHub para integrar los cambios a la rama `main`.
