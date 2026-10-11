# 📡 Guía del Microservicio 3: EnRutate (REST - Estándar Cafetería)

**EnRutate - Sistema Integral de Transporte Público**

**Puerto Asignado:** `5003`  
**Protocolo:** RESTful (JSON)  
**Seguridad:** Autenticación por JWT Bearer Token y API Key (`X-API-KEY: 123`)  
**Estructura:** Idéntica al proyecto de clase `cafeteria_api_GPPD_jwt`  
**Base de Datos:** MySQL (`enrutate_db`)

---

## 🏛️ Estructura de Carpetas (Estándar Cafetería)

```text
microservicios/servicio_monitoreo/
├── config.py             <- Configuración de base de datos, API_KEY ('123') y JWT_SECRET_KEY
├── app.py                <- Inicialización de Flask, Flask-MySQLdb y registro de Blueprints
├── server.py             <- Punto de entrada ejecutable en puerto 5003
├── utils/
│   └── auth.py           <- Decoradores @require_api_key y @require_jwt (idénticos a cafetería)
└── rutas/
    ├── login.py          <- Endpoints POST /register y POST /login (con JWT)
    └── monitoreo.py      <- Las 5 funcionalidades no lineales comprensibles para Popayán
```

---

## 🔐 Autenticación y Seguridad

Siguiendo el estándar de clase:
* **API Key:** Header `X-API-KEY: 123` o query param `?api_key=123`.
* **JWT:** Header `Authorization: Bearer <TOKEN>` obtenido en el login.

### Credenciales de Prueba en Base de Datos:
* **Usuario:** `admin` | **Contraseña:** `admin123`
* **Usuario:** `operador` | **Contraseña:** `operador123`

---

## 🔑 Endpoints de Autenticación

### 1. Registro de Usuario (Protegido con API Key)
* **Método y URL:** `POST http://127.0.0.1:5003/register`
* **Header requerido:** `X-API-KEY: 123`
* **Cuerpo JSON:**
```json
{
  "username": "nuevo_operador",
  "password": "clave123"
}
```
* **Respuesta HTTP 201:** `{"mensaje": "Usuario registrado exitosamente"}`

### 2. Login de Usuario (Retorna Token JWT)
* **Método y URL:** `POST http://127.0.0.1:5003/login`
* **Cuerpo JSON:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```
* **Respuesta HTTP 200:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "tipo": "Bearer",
  "expira_en_minutos": 60,
  "api_key_disponible": "123"
}
```

---

## ⭐ Las 5 Funcionalidades No Lineales Claras para Popayán

Todos los endpoints requieren el header `Authorization: Bearer <token>` o `X-API-KEY: 123`.

---

### 1. Detección de Sobrecupo y Velocidad
* **URL:** `POST http://127.0.0.1:5003/monitoreo/sobrecupo`
* **¿Qué hace?:** Evalúa si una buseta de Popayán (ej. Sotracauca) supera la capacidad de 19 pasajeros y si conduce con exceso de velocidad urbana (>40 km/h). Si hay sobrecupo grave, ordena automáticamente despachar un bus de refuerzo.
* **Petición JSON:**
```json
{
  "placa_bus": "TPK-102",
  "pasajeros_actuales": 24,
  "capacidad_maxima": 19,
  "velocidad_kmh": 46.0
}
```
* **Respuesta HTTP 200:**
```json
{
  "placa_bus": "TPK-102",
  "pasajeros_actuales": 24,
  "capacidad_maxima": 19,
  "porcentaje_ocupacion": "126.3%",
  "exceso_pasajeros": 5,
  "velocidad_registrada_kmh": 46.0,
  "nivel_alerta": "INFRACCION_GRAVE_ALTO_RIESGO",
  "despachar_bus_refuerzo": true,
  "dictamen": "Peligro: Exceso de 5 pasajeros a 46.0 km/h. Conducción riesgosa."
}
```

---

### 2. Tarifa Dinámica con Descuento Escalonado (Estudiantes / Adulto Mayor)
* **URL:** `POST http://127.0.0.1:5003/monitoreo/tarifa-descuento`
* **¿Qué hace?:** Aplica descuentos por tramos no lineales para la comunidad universitaria de Popayán (Unicauca/Colegio Mayor) y tarifa subsidiada plana de $1.800 para adultos mayores.
* **Petición JSON:**
```json
{
  "tipo_usuario": "ESTUDIANTE",
  "cantidad_viajes": 25,
  "tarifa_base": 2800
}
```
* **Respuesta HTTP 200:**
```json
{
  "tipo_usuario": "ESTUDIANTE",
  "cantidad_viajes": 25,
  "tarifa_base_unidad": 2800.0,
  "tarifa_final_por_viaje": 1960.0,
  "total_sin_descuento": 70000.0,
  "total_a_pagar": 49000.0,
  "porcentaje_descuento_aplicado": "30%",
  "ahorro_total_generado": 21000.0,
  "beneficio_obtenido": "Tarifa Universitaria Premium (Abono Mensual Unicauca)"
}
```

---

### 3. Control de Velocidad en Zonas Escolares y Hospitalarias
* **URL:** `POST http://127.0.0.1:5003/monitoreo/control-velocidad`
* **¿Qué hace?:** Verifica que los buses no excedan la velocidad frente a zonas sensibles de Popayán (Hospital San José, colegios, Centro Histórico con límite 30 km/h, o Panamericana con límite 50 km/h) y aplica sanciones por escalas.
* **Petición JSON:**
```json
{
  "placa_bus": "SOT-451",
  "zona": "ZONA_HOSPITALARIA",
  "velocidad_kmh": 48.0
}
```
* **Respuesta HTTP 200:**
```json
{
  "placa_bus": "SOT-451",
  "zona_evaluada": "ZONA_HOSPITALARIA",
  "descripcion_sector": "Sector Hospital San José / Clínicas",
  "velocidad_registrada_kmh": 48.0,
  "limite_maximo_permitido_kmh": 30.0,
  "exceso_de_velocidad_kmh": 18.0,
  "estado_infraccion": "FALTA_GRAVE_ALTO_RIESGO",
  "sancion_aplicable": "Comparendo Tipo C: Multa grave de 15 SMDLV, reporte a Tránsito de Popayán y citación obligatoria a la empresa operadora.",
  "penalizacion_puntos_conductor": 15
}
```

---

### 4. Simulador de Tiempo de Espera en Paradero (Lluvia y Hora Pico)
* **URL:** `POST http://127.0.0.1:5003/monitoreo/tiempo-espera`
* **¿Qué hace?:** Predice los minutos de espera en paraderos reales de Popayán (Campanario, Bolívar) teniendo en cuenta que cuando llueve y es hora pico de la tarde, el tráfico en la variante y el centro colapsa de forma multiplicativa.
* **Petición JSON:**
```json
{
  "paradero": "Campanario",
  "hora": 18,
  "esta_lloviendo": true
}
```
* **Respuesta HTTP 200:**
```json
{
  "paradero_consultado": "Campanario",
  "hora_del_dia": "18:00",
  "condicion_hora_pico": true,
  "presencia_de_lluvia": true,
  "tiempo_estimado_espera_minutos": 29,
  "estado_del_trafico": "COLAPSO_VIAL",
  "recomendacion_pasajero": "Vías de Popayán muy lentas por lluvia y hora pico simultáneas. Salir con 20 minutos de antelación."
}
```

---

### 5. Evaluación de Conductor y Puntos por Reincidencia de Quejas
* **URL:** `POST http://127.0.0.1:5003/monitoreo/evaluar-conductor`
* **¿Qué hace?:** Califica el desempeño de conductores de Sotracauca o Transpubenza. Inicia en 100 puntos, premia con +5 por alta puntualidad, y penaliza fuertemente las quejas recurrentes (la reincidencia resta 15 puntos por cada queja extra).
* **Petición JSON:**
```json
{
  "conductor_nombre": "Jairo Ordonez",
  "empresa": "Sotracauca",
  "viajes_realizados": 50,
  "viajes_a_tiempo": 47,
  "quejas_recibidas": 3
}
```
* **Respuesta HTTP 200:**
```json
{
  "conductor_nombre": "Jairo Ordonez",
  "empresa_transportadora": "Sotracauca",
  "viajes_realizados": 50,
  "porcentaje_puntualidad": "94.0%",
  "quejas_ciudadanas": 3,
  "bono_obtenido": 5,
  "penalizacion_por_quejas": 27,
  "puntaje_final": 78,
  "calificacion_conductor": "CONDUCTOR_BUENO",
  "medida_administrativa": "Desempeño normal en ruta. Sin observaciones."
}
```

---

## 🚀 Cómo Ejecutar

1. Iniciar Microservicio 3 en puerto 5003:
   * Doble clic en `scripts/iniciar_servicio_monitoreo.bat` o:
   ```bash
   cd microservicios\servicio_monitoreo
   ..\..\venv\Scripts\python.exe app.py
   ```
2. Ejecutar la prueba automática:
   ```bash
   .\venv\Scripts\python.exe scripts\probar_servicio_monitoreo.py
   ```
