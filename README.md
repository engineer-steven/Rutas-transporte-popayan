# EnRutate - Transporte público de Popayán

Plataforma basada en **Arquitectura Full-Stack desacoplada** (Frontend Vue.js + Vite y microservicios Flask REST + MySQL) para la gestión de rutas de transporte urbano, analítica avanzada de viajes, control de despachos y alertas en la ciudad de Popayán.

---

## 🚀 Arquitectura Full-Stack (Estándar Clase Unicomfacauca)

Siguiendo la presentación técnica **"Del backend al full-stack" (Presentación 10)** y el patrón implementado en **`cafeteria_Vue`**, el proyecto se encuentra estructurado en dos capas independientes que se comunican exclusivamente mediante HTTP:

```text
proyecto rutas/
├── backend/
│   ├── iniciar_microservicios.py
│   ├── servicio_rutas/
│   ├── servicio_operaciones/
│   └── servicio_monitoreo/
├── frontend/
├── base_de_datos/
└── scripts/
```

---

## ⚡ Puesta en Marcha Rápida

### Configurar la firma de sesiones

Los tres microservicios deben compartir un secreto JWT aleatorio de al menos 32 caracteres. Copia `.env.example` a `.env` en la raíz y reemplaza el valor de `JWT_SECRET_KEY`; puedes generar uno con:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

No reutilices el secreto de ejemplo ni publiques el valor de `.env`. El backend se detiene si falta una clave válida.

Para configurar las URLs locales del frontend, copia `frontend/.env.example` a `frontend/.env`. El archivo `.env` de raíz admite una `API_KEY` opcional para integraciones servidor a servidor; no la pongas en `frontend/.env` ni en una variable `VITE_*`, porque los valores `VITE_*` son visibles en el navegador. La aplicación web se autentica con JWT.

### 1. Iniciar los microservicios (Flask - Puertos 5001, 5002 y 5003)
Doble clic en `scripts/iniciar_backend.bat` o:
```powershell
.\venv\Scripts\python.exe .\backend\iniciar_microservicios.py
```
> APIs disponibles en `http://127.0.0.1:5001`, `http://127.0.0.1:5002` y `http://127.0.0.1:5003`.

### 2. Iniciar el Frontend (Vue 3 + Vite - Puerto 5174)
Doble clic en `scripts/iniciar_frontend.bat` o:
```bash
cd frontend
npm run dev
```
> Aplicación web disponible en: `http://localhost:5174`

### 3. Credenciales de Acceso
* **Usuario:** `admin` | **Contraseña:** `admin123`
* **Usuario:** `operador_popayan` | **Contraseña:** `operador123`

Estas son credenciales de demostración del esquema SQL; cámbialas antes de desplegar el sistema.

### Roles y registro

El formulario público de registro crea únicamente cuentas `USUARIO`; no permite elegir ni enviar otro rol. Los permisos se verifican también en el backend:

| Rol | Acceso |
| --- | --- |
| `ADMIN` | Todas las secciones y acciones administrativas |
| `SUPERVISOR` | Rutas (lectura), operaciones, alertas (lectura), despacho y planificador |
| `OPERADOR` | Rutas (lectura), operaciones, despacho y planificador |
| `USUARIO` | Consulta de rutas y planificador |

Para crear un administrador, registra primero una cuenta normal y luego un administrador de la base de datos debe promoverla directamente en MySQL:

```sql
UPDATE users SET role = 'ADMIN' WHERE username = 'nombre_de_usuario';
```

La aplicación no ofrece autoasignación ni registro público de administradores. Las claves de API guardadas en la base de datos no sustituyen el token JWT para acceder a la aplicación.

---

## 🏛️ Arquitectura Modular del Proyecto

Los servicios se mantienen en una única ubicación, `backend/`, organizados por dominio. Cada microservicio contiene su propia aplicación, configuración, persistencia, lógica y rutas. Los scripts de ejecución están en `scripts/` y el esquema compartido en `base_de_datos/`.

## 📦 Explicación de Cada Archivo dentro de los Microservicios

Cada microservicio cuenta con 6 archivos con responsabilidades estrictamente separadas:

| Archivo             | Capa / Responsabilidad   | ¿Por qué existe y qué hace?                                                                                                                                                                                                                   |
| ------------------- | ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`config.py`**     | **Configuración**        | Lee las credenciales de la base de datos (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`) y el puerto (`SERVER_PORT`) desde variables de entorno con fallbacks por defecto. Evita quemar contraseñas en el código.                            |
| **`database.py`**   | **Conexión a BD**        | Abre conexiones a MySQL usando `pymysql` con `DictCursor`. Provee el context manager `get_cursor(commit=False)` para abrir, ejecutar y cerrar la conexión automáticamente, previniendo fugas de conexiones.                                   |
| **`models.py`**     | **Modelos de datos**     | Define las estructuras de datos utilizadas por las rutas y operaciones que lo requieren.                                                                 |
| **`repository.py`** | **Acceso a datos (DAO)** | Encapsula las consultas SQL y la persistencia en MySQL.                                                                                                    |
| **`service.py`**    | **Lógica de negocio**    | Implementa las reglas, cálculos y algoritmos propios del servicio.                                                                                         |
| **`server.py`**     | **Punto de entrada**     | Inicia la aplicación Flask del microservicio en el puerto configurado.                                                                                     |

---

## 🗄️ Base de Datos: `base_de_datos/esquema_bd.sql`

> **Nota de diseño:** La lógica de conexión reside en el archivo `database.py` de cada microservicio, por lo que la carpeta `base_de_datos/` contiene únicamente el script SQL de creación y datos de prueba.

El esquema incluye 14 recorridos simulados numerados `RUTA-11` a `RUTA-24`, con 85 barrios, sectores y puntos de referencia de Popayán para probar búsquedas, recorridos directos y transbordos. Los nombres de empresas se muestran solo como referencia: no confirman que operen esas rutas. Los trayectos y horarios no son oficiales, y la lista no pretende ser el inventario municipal completo de barrios. Por ejemplo, prueba `La Paz` → `Centro Comercial Campanario` para comparar alternativas, o `Cajete` → `Hospital` para buscar un transbordo.

En las tarjetas de ruta y en un itinerario recomendado, **Ver en Google Maps** abre Google Maps en modo transporte público. Google calcula su propio trayecto; el sistema aún no almacena coordenadas o trazados oficiales para dibujar la línea exacta del bus.

### Tablas del Sistema:

1. **`routes`**: Información de rutas de buses (código, empresa como _Sotracauca_ o _Transpubenza_, origen, destino, tarifa, horario y estado).
2. **`stops`**: Paraderos georreferenciados asociados a cada ruta con orden secuencial (`stop_order`).
3. **`dispatches`**: Despachos de vehículos con placa (`bus_plate`) y fecha/hora de salida (`departure_time`).
4. **`incidents`**: Novedades y alertas viales activas o resueltas (congestión, accidentes, desvíos).

---

## 🚌 Microservicio 1: Servicio de Rutas (Puerto 5001)

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
   - Valida la secuencia direccional de paraderos (`s1.stop_order < s2.stop_order`).
   - Calcula cantidad de paradas intermedias, tiempo estimado de viaje (~4 min por parada) y tarifa.
2. **`suggest_transfer_trip(origin_keyword, destination_keyword)`**:
   - Algoritmo de planificación multimodal con transbordo entre 2 rutas cuando no existe conexión directa.
   - Encuentra el nodo o paradero común de cambio (_Centro/Parque Caldas_ o _Terminal_), calcula tarifa combinada y tiempo total con margen de espera.
3. **`calculate_route_congestion_index(route_id)`**:
   - Cruza la ruta con la tabla de incidentes activos (`incidents`).
   - Aplica ponderaciones por tipo de evento (+20 min accidente, +15 min desvío, +10 min congestión) y calcula el índice de confiabilidad (0-100%) y nivel (_NORMAL_, _MODERADO_, _ALTO_, _CRÍTICO_).
4. **`simulate_traffic_schedule(route_id, departure_hour)`**:
   - Evalúa la hora de salida respecto a las horas pico de Popayán (_06:30–08:30_, _11:45–13:45_, _17:30–19:30_).
   - Aplica factor multiplicador de tráfico del `1.45x` y calcula la hora estimada de llegada con consejos preventivos.
5. **`compare_routes_efficiency(route_id_1, route_id_2)`**:
   - Compara dos rutas evaluando densidad de paraderos, tarifa y tiempo de ciclo completo.
   - Emite un dictamen técnico recomendando cuál es superior según rapidez o economía.

---

## ⏱️ Microservicio 2: Servicio de Operaciones (Puerto 5002)

Gestiona la operativa en vía, intervalos entre despachos de buses y novedades de tránsito:

- `calculate_bus_time_difference(route_id, bus_plate_1, bus_plate_2)`: Consulta los despachos de dos vehículos en una ruta y calcula los minutos exactos de intervalo entre salidas.
- `calculate_time_gap(time_1, time_2)`: Calculadora horaria directa entre dos cadenas de tiempo.
- `get_stops_by_route(route_id)`: Lista los paraderos de una ruta ordenados por su campo `stop_order`.
- `report_incident(route_id, incident_type, description, reported_by)`: Registra un incidente vial en la ruta.
- `get_incidents_by_route(route_id)`: Consulta las novedades viales activas reportadas para una ruta.

---

## 🚀 Puesta en Marcha y Pruebas

### 1. Activar Entorno Virtual e Instalar Dependencias

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Importar Base de Datos en MySQL

Ejecuta el archivo `base_de_datos/esquema_bd.sql` en phpMyAdmin, MySQL Workbench o consola MySQL.

### 3. Ejecutar los Servidores

- **Terminal 1 (Rutas, puerto 5001):**

  ```powershell
  python backend\servicio_rutas\server.py
  ```

  > API: **`http://127.0.0.1:5001/`**

- **Terminal 2 (Operaciones, puerto 5002):**
  ```powershell
  python backend\servicio_operaciones\server.py
  ```
  > API: **`http://127.0.0.1:5002/`**

### 4. Probar las APIs REST

Usa Postman con los endpoints y métodos HTTP definidos en cada servicio. El Microservicio 3 (Monitoreo) se ejecuta en el puerto 5003.
