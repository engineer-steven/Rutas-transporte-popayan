-- ==============================================================================
-- ESQUEMA DE BASE DE DATOS: SISTEMA DE TRANSPORTE PÚBLICO (POPAYÁN)
-- Base de Datos: movi_popayan_db
-- ==============================================================================

-- 1. Crear base de datos
CREATE DATABASE IF NOT EXISTS movi_popayan_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE movi_popayan_db;

-- 2. TABLA routes (Rutas de transporte público de Popayán)
CREATE TABLE IF NOT EXISTS routes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) NOT NULL UNIQUE,
    company VARCHAR(100) NOT NULL,
    origin VARCHAR(150) NOT NULL,
    destination VARCHAR(150) NOT NULL,
    fare DECIMAL(10,2) NOT NULL DEFAULT 2800.00,
    schedule VARCHAR(100) NOT NULL DEFAULT '05:30 - 21:00',
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVA'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. TABLA stops (Paraderos y puntos de referencia de cada ruta)
CREATE TABLE IF NOT EXISTS stops (
    id INT PRIMARY KEY AUTO_INCREMENT,
    route_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    landmark_reference VARCHAR(200),
    stop_order INT NOT NULL,
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. TABLA dispatches (Control de despachos e intervalos entre buses)
CREATE TABLE IF NOT EXISTS dispatches (
    id INT PRIMARY KEY AUTO_INCREMENT,
    route_id INT NOT NULL,
    bus_plate VARCHAR(20) NOT NULL,
    departure_time DATETIME NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'EN_RUTA',
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. TABLA incidents (Reporte de novedades viales, tráfico y desvíos)
CREATE TABLE IF NOT EXISTS incidents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    route_id INT NOT NULL,
    incident_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    reported_by VARCHAR(100) NOT NULL,
    reported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVO',
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ==============================================================================
-- DATOS INICIALES DE PRUEBA (POPAYÁN)
-- ==============================================================================

-- Rutas
INSERT INTO routes (id, code, company, origin, destination, fare, schedule, status) VALUES
(1, 'RUTA-1', 'Sotracauca', 'Barrio Bolívar', 'Campanario / Variante Norte', 2800.00, '05:30 - 21:30', 'ACTIVA'),
(2, 'LINEA-2', 'Transpubenza', 'Lomas de Granada', 'Terminal de Transportes', 2800.00, '06:00 - 21:00', 'ACTIVA'),
(3, 'RUTA-5', 'Translibertad', 'Bello Horizonte', 'Hospital San José / Centro', 2900.00, '05:45 - 20:45', 'ACTIVA'),
(4, 'RUTA-9', 'Sotracauca', 'Terminal de Transportes', 'Variante Norte / Campanario', 2800.00, '06:00 - 22:00', 'ACTIVA')
ON DUPLICATE KEY UPDATE code=VALUES(code);

-- Paraderos de la Ruta 1 (Barrio Bolívar -> Campanario)
INSERT INTO stops (route_id, name, landmark_reference, stop_order) VALUES
(1, 'Paradero Barrio Bolívar', 'Frente a galería Bolívar', 1),
(1, 'Parque Caldas - Centro', 'Carrera 6 con Calle 4', 2),
(1, 'Hospital Universitario San José', 'Urgencias Calle 5', 3),
(1, 'Centro Comercial Campanario', 'Entrada principal Panamericana', 4),
(1, 'Variante Norte', 'Frente a Makro Popayán', 5);

-- Paraderos de la Ruta 2 (Lomas de Granada -> Terminal)
INSERT INTO stops (route_id, name, landmark_reference, stop_order) VALUES
(2, 'Lomas de Granada', 'Entrada sector 3', 1),
(2, 'Barrio La Esmeralda', 'Frente a droguería La Economía', 2),
(2, 'Parque Caldas - Centro', 'Carrera 7 con Calle 5', 3),
(2, 'Terminal de Transportes', 'Bahía de desembarque taquillas', 4);

-- Paraderos de la Ruta 5 (Bello Horizonte -> Hospital San José)
INSERT INTO stops (route_id, name, landmark_reference, stop_order) VALUES
(3, 'Bello Horizonte', 'Cerca a polideportivo norte', 1),
(3, 'Centro Comercial Campanario', 'Frente a Olímpica', 2),
(3, 'Hospital Universitario San José', 'Entrada consulta externa', 3);

-- Paraderos de la Ruta 9 (Terminal -> Variante Norte)
INSERT INTO stops (route_id, name, landmark_reference, stop_order) VALUES
(4, 'Terminal de Transportes', 'Bahía principal', 1),
(4, 'Centro Comercial Campanario', 'Entrada Panamericana', 2),
(4, 'Variante Norte', 'Glorieta Chirimía norte', 3);

-- Despachos de prueba (con soporte de fecha y hora completa)
INSERT INTO dispatches (route_id, bus_plate, departure_time, status) VALUES
(1, 'TPK-101', '2026-09-02 06:30:00', 'FINALIZADO'),
(1, 'TPK-102', '2026-09-02 06:48:00', 'EN_RUTA'),
(1, 'TPK-103', '2026-09-02 07:05:00', 'EN_RUTA'),
(2, 'SOT-205', '2026-09-02 07:15:00', 'EN_RUTA'),
(2, 'SOT-206', '2026-09-02 07:35:00', 'EN_RUTA');

-- Incidentes viales de prueba
INSERT INTO incidents (route_id, incident_type, description, reported_by, status) VALUES
(1, 'CONGESTION', 'Tráfico denso y paso restringido en la Carrera 6 cerca a la galería Bolívar', 'Operador Central Sotracauca', 'ACTIVO'),
(2, 'DESVIO', 'Cierre parcial temporal por pavimentación en vía La Esmeralda', 'Tránsito Municipal Popayán', 'ACTIVO');
