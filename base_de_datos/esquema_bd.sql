-- ==============================================================================
-- ESQUEMA DE BASE DE DATOS: SISTEMA DE TRANSPORTE PÚBLICO (POPAYÁN)
-- Base de Datos: movi_popayan_db
-- ==============================================================================

-- 1. Crear la base de datos y seleccionarla
CREATE DATABASE IF NOT EXISTS movi_popayan_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE movi_popayan_db;

-- 2. Crear la tabla `routes`
CREATE TABLE IF NOT EXISTS routes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) NOT NULL,
    company VARCHAR(100) NOT NULL,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    fare DECIMAL(10,2) NOT NULL,
    schedule VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL
);

-- 3. Crear la tabla `stops`
CREATE TABLE IF NOT EXISTS stops (
    id INT PRIMARY KEY AUTO_INCREMENT,
    route_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    landmark_reference VARCHAR(150),
    stop_order INT NOT NULL,
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
);

-- 4. Crear la tabla `dispatches`
CREATE TABLE IF NOT EXISTS dispatches (
    id INT PRIMARY KEY AUTO_INCREMENT,
    route_id INT NOT NULL,
    bus_plate VARCHAR(20) NOT NULL,
    departure_time DATETIME NOT NULL,
    status VARCHAR(50) NOT NULL,
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
);

-- 5. Crear la tabla `incidents`
CREATE TABLE IF NOT EXISTS incidents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    route_id INT NOT NULL,
    incident_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    reported_by VARCHAR(100) NOT NULL,
    reported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
);

-- 6. INSERTAR DATOS DE PRUEBA
INSERT INTO routes (code, company, origin, destination, fare, schedule, status) VALUES
('RUTA-1', 'Sotracauca', 'Barrio Bolívar', 'Campanario / Variante', 2500.00, '05:30 - 21:00', 'ACTIVA'),
('RUTA-2', 'Transpubenza', 'Lomas de Granada', 'Pandiguando', 2500.00, '06:00 - 20:30', 'ACTIVA'),
('RUTA-5', 'Sotracauca', 'La Esmeralda', 'Terminal de Transportes', 2500.00, '05:00 - 22:00', 'ACTIVA');

INSERT INTO stops (route_id, name, landmark_reference, stop_order) VALUES
(1, 'Barrio Bolívar', 'Zona comercial central', 1),
(1, 'Parque Caldas', 'Plazoleta principal', 2),
(1, 'Centro Comercial Campanario', 'Frente a la entrada principal', 3),
(2, 'Lomas de Granada', 'Entrada principal etapa 1', 1),
(2, 'Puente del Humilladero', 'Sector histórico', 2),
(3, 'La Esmeralda', 'Cancha principal', 1),
(3, 'Terminal de Transportes', 'Frente a taquillas', 2);

INSERT INTO dispatches (route_id, bus_plate, departure_time, status) VALUES
(1, 'TPK-102', '2026-09-02 06:30:00', 'EN_RUTA'),
(2, 'SOT-451', '2026-09-02 07:00:00', 'FINALIZADO'),
(3, 'TPB-890', '2026-09-02 07:15:00', 'EN_RUTA');

INSERT INTO incidents (route_id, incident_type, description, reported_by, status) VALUES
(1, 'CONGESTION', 'Tráfico pesado en el sector del centro histórico por obras viales.', 'Conductor', 'ACTIVO'),
(2, 'DESVIO', 'Cierre temporal de vía cerca al puente por manifestación.', 'Pasajero', 'RESUELTO');