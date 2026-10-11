-- ==============================================================================
-- ESQUEMA DE BASE DE DATOS: SISTEMA DE TRANSPORTE PÚBLICO (POPAYÁN)
-- Base de Datos: enrutate_db
-- ==============================================================================

-- 1. Crear base de datos
CREATE DATABASE IF NOT EXISTS enrutate_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE enrutate_db;

-- 2. TABLA rutas (Rutas de transporte público de Popayán)
CREATE TABLE IF NOT EXISTS rutas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) NOT NULL UNIQUE,
    company VARCHAR(100) NOT NULL,
    origin VARCHAR(150) NOT NULL,
    destination VARCHAR(150) NOT NULL,
    fare DECIMAL(10,2) NOT NULL DEFAULT 3000.00,
    schedule VARCHAR(100) NOT NULL DEFAULT '05:30 - 21:00',
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVA'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. TABLA paradas (Paraderos y puntos de referencia de cada ruta)
CREATE TABLE IF NOT EXISTS paradas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    route_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    landmark_reference VARCHAR(200),
    stop_order INT NOT NULL,
    FOREIGN KEY (route_id) REFERENCES rutas(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. TABLA despachos (Control de despachos e intervalos entre buses)
CREATE TABLE IF NOT EXISTS despachos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    route_id INT NOT NULL,
    bus_plate VARCHAR(20) NOT NULL,
    departure_time DATETIME NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'EN_RUTA',
    FOREIGN KEY (route_id) REFERENCES rutas(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. TABLA incidentes (Reporte de novedades viales, tráfico y desvíos)
CREATE TABLE IF NOT EXISTS incidentes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    route_id INT NOT NULL,
    incident_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    reported_by VARCHAR(100) NOT NULL,
    reported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVO',
    FOREIGN KEY (route_id) REFERENCES rutas(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- 6. DATOS INICIALES DE PRUEBA (POPAYÁN) — un solo set, sin duplicados
-- ==============================================================================

-- Rutas (Tarifa Popayán: Urbana $3.000 COP / Vereda cercana $3.200 / Vereda lejana $3.400)
INSERT INTO rutas (id, code, company, origin, destination, fare, schedule, status) VALUES
(1, 'RUTA-1', 'Sotracauca', 'Barrio Bolívar', 'Campanario / Variante Norte', 3000.00, '05:30 - 21:30', 'ACTIVA'),
(2, 'LINEA-2', 'Transpubenza', 'Lomas de Granada', 'Terminal de Transportes', 3000.00, '06:00 - 21:00', 'ACTIVA'),
(3, 'RUTA-5', 'Translibertad', 'Bello Horizonte', 'Hospital San José / Centro', 3000.00, '05:45 - 20:45', 'ACTIVA'),
(4, 'RUTA-9', 'Sotracauca', 'Terminal de Transportes', 'Variante Norte / Campanario', 3000.00, '06:00 - 22:00', 'ACTIVA'),
(5, 'TL1BT', 'Translibertad', 'Calle 5', 'Calle 5', 3000.00, '05:00 - 21:30', 'ACTIVA'),
(6, 'TT1M', 'Transtambo', 'Cajete', 'Pisojé', 3400.00, '05:30 - 20:00', 'ACTIVA')
ON DUPLICATE KEY UPDATE code=VALUES(code);

-- Rutas adicionales reales de Popayán
INSERT INTO rutas (id, code, company, origin, destination, fare, schedule, status) VALUES
(7,  'TP1BT', 'Transpubenza', 'La Paz', 'Los Naranjos', 3000.00, '05:30 - 21:00', 'ACTIVA'),
(8,  'TP9BT', 'Transpubenza', 'Lomas de Granada', 'La Venta', 3200.00, '05:30 - 21:00', 'ACTIVA'),
(9,  'SC1M',  'Sotracauca', 'Calle 72 Norte', 'Calle 72 Norte', 3000.00, '05:00 - 22:00', 'ACTIVA'),
(10, 'SC7M',  'Sotracauca', 'Piendamó', 'Santa Teresa', 3400.00, '05:00 - 22:00', 'ACTIVA')
ON DUPLICATE KEY UPDATE code=VALUES(code);


-- Paraderos de la Ruta 1 (Barrio Bolívar -> Campanario)
INSERT INTO paradas (route_id, name, landmark_reference, stop_order) VALUES
(1, 'La Paz', 'Barrio La Paz', 1),
(1, 'La Esmeralda', 'Galería La Esmeralda', 2),
(1, 'Tomas Cipriano', 'Sector Tomas Cipriano', 3),
(1, 'Los Naranjos', 'Barrio Los Naranjos', 4),
(2, 'Lomas de Granada', 'Entrada principal etapa 1', 1),
(2, 'Los Naranjos', 'Barrio Los Naranjos', 2),
(2, 'Centro', 'Carrera 6ª / 7ª', 3),
(2, 'La Venta', 'Sector La Venta', 4),
(3, 'Calle 72 Norte', 'Anillo vial norte', 1),
(4, 'Comuna 1', 'Zona urbana norte', 1),
(4, 'La Esmeralda', 'Galería La Esmeralda', 2),
(4, 'Santa Teresa', 'Sector Santa Teresa', 3),
(5, 'Calle 5', 'Eje vial Calle 5', 1),
(5, 'Comuna 2', 'Zona norte', 2),
(6, 'Cajete', 'Vereda Cajete', 1),
(6, 'Lomas de Granada', 'Entrada principal etapa 1', 2),
(6, 'Galería La Esmeralda', 'Terminal de buses colectivos', 3),
(6, 'Pisojé', 'Vereda Pisojé', 4);

-- Paraderos de la Ruta 2 (Lomas de Granada -> Terminal)
INSERT INTO paradas (route_id, name, landmark_reference, stop_order) VALUES
(2, 'Lomas de Granada', 'Entrada sector 3', 1),
(2, 'Barrio La Esmeralda', 'Frente a droguería La Economía', 2),
(2, 'Parque Caldas - Centro', 'Carrera 7 con Calle 5', 3),
(2, 'Terminal de Transportes', 'Bahía de desembarque taquillas', 4);

-- Paraderos de la Ruta 5 (Bello Horizonte -> Hospital San José)
INSERT INTO paradas (route_id, name, landmark_reference, stop_order) VALUES
(3, 'Bello Horizonte', 'Cerca a polideportivo norte', 1),
(3, 'Centro Comercial Campanario', 'Frente a Olímpica', 2),
(3, 'Hospital Universitario San José', 'Entrada consulta externa', 3);

-- Paraderos de la Ruta 9 (Terminal -> Variante Norte)
INSERT INTO paradas (route_id, name, landmark_reference, stop_order) VALUES
(4, 'Terminal de Transportes', 'Bahía principal', 1),
(4, 'Centro Comercial Campanario', 'Entrada Panamericana', 2),
(4, 'Variante Norte', 'Glorieta Chirimía norte', 3);

-- Despachos de prueba (con soporte de fecha y hora completa)
INSERT INTO despachos (route_id, bus_plate, departure_time, status) VALUES
(1, 'TPK-102', '2026-09-02 06:30:00', 'EN_RUTA'),
(3, 'SOT-451', '2026-09-02 07:00:00', 'FINALIZADO'),
(6, 'TPB-890', '2026-09-02 07:15:00', 'EN_RUTA');

-- Incidentes viales de prueba
INSERT INTO incidentes (route_id, incident_type, description, reported_by, status) VALUES
(1, 'CONGESTION', 'Tráfico pesado en el sector del centro histórico por obras viales.', 'Conductor', 'ACTIVO'),
(5, 'DESVIO', 'Cierre temporal de vía cerca al puente por manifestación.', 'Pasajero', 'RESUELTO');

-- ==============================================================================
-- 6. TABLA usuarios (Usuarios para autenticación JWT y Login - Estándar Cafetería)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

-- TABLA usuarios_api (Soporte adicional con rol y API Key)
CREATE TABLE IF NOT EXISTS usuarios_api (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL DEFAULT 'Usuario del Sistema',
    role VARCHAR(50) NOT NULL DEFAULT 'OPERADOR',
    api_key VARCHAR(100) NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- 7. TABLA calificaciones_servicio (Calificaciones de calidad y satisfacción del usuario)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS calificaciones_servicio (
    id INT PRIMARY KEY AUTO_INCREMENT,
    route_id INT NOT NULL,
    company VARCHAR(100) NOT NULL,
    user_id INT NULL,
    punctuality_score INT NOT NULL,
    comfort_score INT NOT NULL,
    driver_score INT NOT NULL,
    safety_score INT NOT NULL,
    final_score DECIMAL(5,2) NOT NULL,
    category VARCHAR(50) NOT NULL,
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (route_id) REFERENCES rutas(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES usuarios_api(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- 8. TABLA telemetria_buses (Telemetría de pasajeros, velocidad y sobrecupo)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS telemetria_buses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    route_id INT NOT NULL,
    bus_plate VARCHAR(20) NOT NULL,
    current_passengers INT NOT NULL,
    max_capacity INT NOT NULL,
    occupancy_ratio DECIMAL(5,2) NOT NULL,
    current_speed DECIMAL(5,2) NOT NULL,
    risk_level VARCHAR(50) NOT NULL,
    reinforcement_needed BOOLEAN NOT NULL DEFAULT FALSE,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (route_id) REFERENCES rutas(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- 9. TABLA alertas_emergencia (Novedades críticas, botón de pánico y seguridad)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS alertas_emergencia (
    id INT PRIMARY KEY AUTO_INCREMENT,
    route_id INT NOT NULL,
    bus_plate VARCHAR(20) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity_level VARCHAR(50) NOT NULL,
    criticality_score DECIMAL(5,2) NOT NULL,
    max_response_time_minutes INT NOT NULL,
    location_landmark VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVA',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (route_id) REFERENCES rutas(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- INSERTS ADICIONALES: MICROSERVICIO 3 (SEGURIDAD, MONITOREO Y TELEMETRÍA)
-- ==============================================================================

-- Usuarios de prueba con hashes SHA-256 y API Keys
-- 1. Usuarios para autenticación JWT y Login (Modelo Cafetería)
-- Credenciales por defecto: admin / admin123  y  operador / operador123
INSERT INTO usuarios (id, username, password_hash) VALUES
(1, 'admin', 'scrypt:32768:8:1$YbEMYh3zpMsluUTs$3b169bd5a8b53189f3bc49a88e07f1ced549b57f58525514a62b140cf4dceb77470dbeef2e4399435a5d4b1b652678731cb0979d6095927ba757f77d3897c7aa'),
(2, 'operador', 'scrypt:32768:8:1$YbEMYh3zpMsluUTs$3b169bd5a8b53189f3bc49a88e07f1ced549b57f58525514a62b140cf4dceb77470dbeef2e4399435a5d4b1b652678731cb0979d6095927ba757f77d3897c7aa')
ON DUPLICATE KEY UPDATE username=VALUES(username);

INSERT INTO usuarios_api (id, username, password_hash, full_name, role, api_key) VALUES
(1, 'admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Administrador del Sistema Popayán', 'ADMIN', 'popayan-admin-key-2026'),
(2, 'operador_popayan', '1725165c9a0b3698a3d01016e0d8205155820b8d7f21835ca64c0f81c728d880', 'Carlos Meneses - Despachos Popayán', 'OPERADOR', 'popayan-operador-key-2026'),
(3, 'conductor_sotracauca', 'c4e047f954c38b86855c1c4ccea7a803f6ccec690954f68731021950bd29c0a7', 'Jairo Ordóñez - Conductor Colectivo', 'CONDUCTOR', 'popayan-conductor-key-2026'),
(4, 'ciudadano_cauca', 'c463ff27738fa30cd49b8546661c9c652f8c14272a35eb8869698198be53ed96', 'María Fernanda López - Usuaria', 'PASAJERO', 'popayan-pasajero-key-2026')
ON DUPLICATE KEY UPDATE username=VALUES(username);

-- Evaluaciones de calidad de prueba
INSERT INTO calificaciones_servicio (route_id, company, user_id, punctuality_score, comfort_score, driver_score, safety_score, final_score, category, comment) VALUES
(1, 'Sotracauca', 4, 4, 4, 5, 5, 91.00, 'EXCELENTE', 'Muy buen recorrido hacia la variante norte, bus limpio.'),
(1, 'Sotracauca', 4, 4, 3, 4, 4, 76.50, 'BUENO', 'Cumplió los tiempos en el Barrio Bolívar.'),
(2, 'Transpubenza', 4, 3, 3, 2, 3, 52.00, 'REGULAR_PLAN_MEJORA', 'El conductor manejaba con afán cerca al Centro Histórico.'),
(3, 'Translibertad', 4, 5, 4, 4, 5, 89.00, 'EXCELENTE', 'Excelente servicio hacia el Hospital San José.'),
(5, 'Translibertad', 4, 2, 2, 2, 2, 35.00, 'CRITICO_SANCIONABLE', 'Mucha demora en Calle 5 y exceso de ruido.');

-- Telemetría de aforo y sobrecupo de prueba
INSERT INTO telemetria_buses (route_id, bus_plate, current_passengers, max_capacity, occupancy_ratio, current_speed, risk_level, reinforcement_needed) VALUES
(1, 'TPK-102', 17, 19, 0.89, 32.5, 'PRECAUCION', 0),
(1, 'TPK-102', 23, 19, 1.21, 46.0, 'INFRACCION_GRAVE_ALTO_RIESGO', 1),
(3, 'SOT-451', 12, 19, 0.63, 28.0, 'NORMAL', 0),
(6, 'TPB-890', 21, 19, 1.11, 35.0, 'SOBRECUPO_CRITICO', 1);

-- Alertas de emergencia de prueba
INSERT INTO alertas_emergencia (route_id, bus_plate, alert_type, severity_level, criticality_score, max_response_time_minutes, location_landmark, description, status) VALUES
(1, 'TPK-102', 'BOTON_PANICO', 'ALTA', 86.25, 9, 'Barrio Bolívar', 'Alerta silenciosa activada por riña en paradero comercial.', 'ACTIVA'),
(2, 'TPB-111', 'ACCIDENTE_VIAL', 'CRITICA', 97.50, 7, 'Parque Caldas - Centro', 'Colisión leve con motocicleta en Carrera 7, paso cerrado.', 'ACTIVA'),
(3, 'SOT-451', 'FALLA_MECANICA', 'MEDIA', 47.50, 28, 'Bello Horizonte', 'Recalentamiento del motor en subida, pasajeros transbordados.', 'RESUELTA');
