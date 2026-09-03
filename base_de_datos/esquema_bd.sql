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

-- 6. INSERTAR DATOS (rutas reales de Popayán: Transpubenza, Sotracauca, Translibertad, Transtambo)
INSERT INTO routes (code, company, origin, destination, fare, schedule, status) VALUES
('TP1BT', 'Transpubenza', 'La Paz', 'Los Naranjos', 2500.00, '05:30 - 21:00', 'ACTIVA'),
('TP9BT', 'Transpubenza', 'Lomas de Granada', 'La Venta', 2500.00, '05:30 - 21:00', 'ACTIVA'),
('SC1M', 'Sotracauca', 'Calle 72 Norte', 'Calle 72 Norte', 2500.00, '05:00 - 22:00', 'ACTIVA'),
('SC7M', 'Sotracauca', 'Piendamó', 'Santa Teresa', 2500.00, '05:00 - 22:00', 'ACTIVA'),
('TL1BT', 'Translibertad', 'Calle 5', 'Calle 5', 2500.00, '05:00 - 21:30', 'ACTIVA'),
('TT1M', 'Transtambo', 'Cajete', 'Pisojé', 2500.00, '05:30 - 20:00', 'ACTIVA');

INSERT INTO stops (route_id, name, landmark_reference, stop_order) VALUES
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

INSERT INTO dispatches (route_id, bus_plate, departure_time, status) VALUES
(1, 'TPK-102', '2026-09-02 06:30:00', 'EN_RUTA'),
(3, 'SOT-451', '2026-09-02 07:00:00', 'FINALIZADO'),
(6, 'TPB-890', '2026-09-02 07:15:00', 'EN_RUTA');

INSERT INTO incidents (route_id, incident_type, description, reported_by, status) VALUES
(1, 'CONGESTION', 'Tráfico pesado en el sector del centro histórico por obras viales.', 'Conductor', 'ACTIVO'),
(5, 'DESVIO', 'Cierre temporal de vía cerca al puente por manifestación.', 'Pasajero', 'RESUELTO');