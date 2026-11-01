-- ==============================================================================
-- ESQUEMA DE BASE DE DATOS: SISTEMA DE TRANSPORTE PÚBLICO (POPAYÁN)
-- Base de Datos: Enrutate
-- ==============================================================================

-- 1. Crear base de datos
CREATE DATABASE IF NOT EXISTS Enrutate CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE Enrutate;

-- 2. TABLA routes (Rutas de transporte público de Popayán)
CREATE TABLE IF NOT EXISTS routes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) NOT NULL UNIQUE,
    company VARCHAR(100) NOT NULL,
    origin VARCHAR(150) NOT NULL,
    destination VARCHAR(150) NOT NULL,
    fare DECIMAL(10,2) NOT NULL DEFAULT 3000.00,
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

-- Rutas (Tarifa Popayán: Urbana $3.000 COP / Vereda cercana $3.200 / Vereda lejana $3.400)
INSERT INTO routes (id, code, company, origin, destination, fare, schedule, status) VALUES
(1, 'RUTA-1', 'Sotracauca', 'Barrio Bolívar', 'Campanario / Variante Norte', 3000.00, '05:30 - 21:30', 'ACTIVA'),
(2, 'LINEA-2', 'Transpubenza', 'Lomas de Granada', 'Terminal de Transportes', 3000.00, '06:00 - 21:00', 'ACTIVA'),
(3, 'RUTA-5', 'Translibertad', 'Bello Horizonte', 'Hospital San José / Centro', 3000.00, '05:45 - 20:45', 'ACTIVA'),
(4, 'RUTA-9', 'Sotracauca', 'Terminal de Transportes', 'Variante Norte / Campanario', 3000.00, '06:00 - 22:00', 'ACTIVA'),
(5, 'TL1BT', 'Translibertad', 'Calle 5', 'Calle 5', 3000.00, '05:00 - 21:30', 'ACTIVA'),
(6, 'TT1M', 'Transtambo', 'Cajete', 'Pisojé', 3400.00, '05:30 - 20:00', 'ACTIVA')
ON DUPLICATE KEY UPDATE code=VALUES(code);

-- Rutas adicionales reales de Popayán
INSERT INTO routes (id, code, company, origin, destination, fare, schedule, status) VALUES
(7,  'TP1BT', 'Transpubenza', 'La Paz', 'Los Naranjos', 3000.00, '05:30 - 21:00', 'ACTIVA'),
(8,  'TP9BT', 'Transpubenza', 'Lomas de Granada', 'La Venta', 3200.00, '05:30 - 21:00', 'ACTIVA'),
(9,  'SC1M',  'Sotracauca', 'Calle 72 Norte', 'Calle 72 Norte', 3000.00, '05:00 - 22:00', 'ACTIVA'),
(10, 'SC7M',  'Sotracauca', 'Piendamó', 'Santa Teresa', 3400.00, '05:00 - 22:00', 'ACTIVA')
ON DUPLICATE KEY UPDATE code=VALUES(code);


-- Paraderos de la Ruta 1 (Barrio Bolívar -> Campanario)
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

-- Rutas y paraderos sintéticos para probar búsquedas directas, transbordos y comparativas.
-- No representan trazados, horarios ni servicios oficiales de transporte.
UPDATE routes
SET code = CASE code
    WHEN 'DEMO-01' THEN 'RUTA-11'
    WHEN 'DEMO-02' THEN 'RUTA-12'
    WHEN 'DEMO-03' THEN 'RUTA-13'
    WHEN 'DEMO-04' THEN 'RUTA-14'
    WHEN 'DEMO-05' THEN 'RUTA-15'
    WHEN 'DEMO-06' THEN 'RUTA-16'
    WHEN 'DEMO-07' THEN 'RUTA-17'
    WHEN 'DEMO-08' THEN 'RUTA-18'
    WHEN 'DEMO-09' THEN 'RUTA-19'
    WHEN 'DEMO-10' THEN 'RUTA-20'
    WHEN 'DEMO-11' THEN 'RUTA-21'
    WHEN 'DEMO-12' THEN 'RUTA-22'
    WHEN 'DEMO-13' THEN 'RUTA-23'
    WHEN 'DEMO-14' THEN 'RUTA-24'
    ELSE code
END
WHERE code IN (
    'DEMO-01', 'DEMO-02', 'DEMO-03', 'DEMO-04', 'DEMO-05', 'DEMO-06', 'DEMO-07',
    'DEMO-08', 'DEMO-09', 'DEMO-10', 'DEMO-11', 'DEMO-12', 'DEMO-13', 'DEMO-14'
);

INSERT INTO routes (code, company, origin, destination, fare, schedule, status) VALUES
('RUTA-11', 'Sotracauca', 'La Paz', 'La Florida', 3000.00, '05:30 - 21:00', 'ACTIVA'),
('RUTA-12', 'Transpubenza', 'La Paz', 'La Cabaña', 3000.00, '05:30 - 21:00', 'ACTIVA'),
('RUTA-13', 'Translibertad', 'La Paz', 'San Antonio', 3200.00, '06:00 - 20:30', 'ACTIVA'),
('RUTA-14', 'Transtambo', 'Lomas de Granada', 'La Unión', 3000.00, '05:45 - 21:00', 'ACTIVA'),
('RUTA-15', 'Sotracauca', 'Cajete', 'Las Tres Margaritas', 3400.00, '05:30 - 20:00', 'ACTIVA'),
('RUTA-16', 'Transpubenza', 'Terminal de Transportes', 'Villa Occidente', 3000.00, '06:00 - 21:00', 'ACTIVA'),
('RUTA-17', 'Translibertad', 'Pueblillo', 'Santa Helena', 3200.00, '05:45 - 20:30', 'ACTIVA'),
('RUTA-18', 'Transtambo', 'Julumito', 'Los Tejares', 3400.00, '05:30 - 19:30', 'ACTIVA'),
('RUTA-19', 'Sotracauca', 'El Uvo', 'Campo Bello', 3000.00, '05:30 - 21:00', 'ACTIVA'),
('RUTA-20', 'Transpubenza', 'Santa Teresa', 'La Capitana', 3200.00, '05:45 - 20:30', 'ACTIVA'),
('RUTA-21', 'Translibertad', 'El Uvo', 'Los Comuneros', 3000.00, '05:30 - 21:00', 'ACTIVA'),
('RUTA-22', 'Transtambo', 'Cajete', 'Las Tres Margaritas', 3400.00, '05:30 - 20:00', 'ACTIVA'),
('RUTA-23', 'Sotracauca', 'Piendamó', 'La Cabaña', 3400.00, '05:00 - 19:00', 'ACTIVA'),
('RUTA-24', 'Transpubenza', 'La Paz', 'La Estancia', 3400.00, '06:00 - 20:00', 'ACTIVA')
ON DUPLICATE KEY UPDATE
    company = VALUES(company),
    origin = VALUES(origin),
    destination = VALUES(destination),
    fare = VALUES(fare),
    schedule = VALUES(schedule),
    status = VALUES(status);

INSERT INTO stops (route_id, name, landmark_reference, stop_order)
SELECT r.id, demo.name, demo.landmark_reference, demo.stop_order
FROM routes r
JOIN (
    SELECT 'DEMO-01' AS code, 'La Paz' AS name, 'Paradero de prueba en La Paz' AS landmark_reference, 1 AS stop_order
    UNION ALL SELECT 'DEMO-01', 'Los Naranjos', 'Paradero de prueba en Los Naranjos', 2
    UNION ALL SELECT 'DEMO-01', 'Centro', 'Paradero de prueba en el Centro', 3
    UNION ALL SELECT 'DEMO-01', 'Terminal de Transportes', 'Paradero de prueba en la Terminal', 4
    UNION ALL SELECT 'DEMO-01', 'Hospital Universitario San José', 'Paradero de prueba en el Hospital San José', 5
    UNION ALL SELECT 'DEMO-02', 'La Paz', 'Paradero de prueba en La Paz', 1
    UNION ALL SELECT 'DEMO-02', 'La Esmeralda', 'Paradero de prueba en La Esmeralda', 2
    UNION ALL SELECT 'DEMO-02', 'Los Naranjos', 'Paradero de prueba en Los Naranjos', 3
    UNION ALL SELECT 'DEMO-02', 'Centro', 'Paradero de prueba en el Centro', 4
    UNION ALL SELECT 'DEMO-02', 'Centro Comercial Campanario', 'Paradero de prueba en Campanario', 5
    UNION ALL SELECT 'DEMO-03', 'La Paz', 'Paradero de prueba en La Paz', 1
    UNION ALL SELECT 'DEMO-03', 'Centro', 'Paradero de prueba en el Centro', 2
    UNION ALL SELECT 'DEMO-03', 'Centro Comercial Campanario', 'Paradero de prueba en Campanario', 3
    UNION ALL SELECT 'DEMO-04', 'Lomas de Granada', 'Paradero de prueba en Lomas de Granada', 1
    UNION ALL SELECT 'DEMO-04', 'Los Naranjos', 'Paradero de prueba en Los Naranjos', 2
    UNION ALL SELECT 'DEMO-04', 'Centro', 'Paradero de prueba en el Centro', 3
    UNION ALL SELECT 'DEMO-04', 'Hospital Universitario San José', 'Paradero de prueba en el Hospital San José', 4
    UNION ALL SELECT 'DEMO-05', 'Cajete', 'Paradero de prueba en Cajete', 1
    UNION ALL SELECT 'DEMO-05', 'Lomas de Granada', 'Paradero de prueba en Lomas de Granada', 2
    UNION ALL SELECT 'DEMO-05', 'Los Naranjos', 'Paradero de prueba en Los Naranjos', 3
    UNION ALL SELECT 'DEMO-05', 'Centro', 'Paradero de prueba en el Centro', 4
    UNION ALL SELECT 'DEMO-05', 'Terminal de Transportes', 'Paradero de prueba en la Terminal', 5
    UNION ALL SELECT 'DEMO-06', 'Terminal de Transportes', 'Paradero de prueba en la Terminal', 1
    UNION ALL SELECT 'DEMO-06', 'Centro', 'Paradero de prueba en el Centro', 2
    UNION ALL SELECT 'DEMO-06', 'Centro Comercial Campanario', 'Paradero de prueba en Campanario', 3
    UNION ALL SELECT 'DEMO-06', 'Bello Horizonte', 'Paradero de prueba en Bello Horizonte', 4
    UNION ALL SELECT 'DEMO-07', 'Pueblillo', 'Paradero de prueba en Pueblillo', 1
    UNION ALL SELECT 'DEMO-07', 'Centro', 'Paradero de prueba en el Centro', 2
    UNION ALL SELECT 'DEMO-07', 'Hospital Universitario San José', 'Paradero de prueba en el Hospital San José', 3
    UNION ALL SELECT 'DEMO-08', 'Julumito', 'Paradero de prueba en Julumito', 1
    UNION ALL SELECT 'DEMO-08', 'La Esmeralda', 'Paradero de prueba en La Esmeralda', 2
    UNION ALL SELECT 'DEMO-08', 'Centro', 'Paradero de prueba en el Centro', 3
    UNION ALL SELECT 'DEMO-08', 'Centro Comercial Campanario', 'Paradero de prueba en Campanario', 4
    UNION ALL SELECT 'DEMO-09', 'El Uvo', 'Paradero de prueba en El Uvo', 1
    UNION ALL SELECT 'DEMO-09', 'Centro', 'Paradero de prueba en el Centro', 2
    UNION ALL SELECT 'DEMO-09', 'Alfonso López', 'Paradero de prueba en Alfonso López', 3
    UNION ALL SELECT 'DEMO-10', 'Santa Teresa', 'Paradero de prueba en Santa Teresa', 1
    UNION ALL SELECT 'DEMO-10', 'Centro', 'Paradero de prueba en el Centro', 2
    UNION ALL SELECT 'DEMO-10', 'Los Naranjos', 'Paradero de prueba en Los Naranjos', 3
    UNION ALL SELECT 'DEMO-10', 'La Paz', 'Paradero de prueba en La Paz', 4
    UNION ALL SELECT 'DEMO-11', 'El Uvo', 'Paradero de prueba en El Uvo', 1
    UNION ALL SELECT 'DEMO-11', 'Centro', 'Paradero de prueba en el Centro', 2
    UNION ALL SELECT 'DEMO-11', 'Terminal de Transportes', 'Paradero de prueba en la Terminal', 3
    UNION ALL SELECT 'DEMO-12', 'Cajete', 'Paradero de prueba en Cajete', 1
    UNION ALL SELECT 'DEMO-12', 'Lomas de Granada', 'Paradero de prueba en Lomas de Granada', 2
    UNION ALL SELECT 'DEMO-12', 'Centro', 'Paradero de prueba en el Centro', 3
    UNION ALL SELECT 'DEMO-12', 'Los Naranjos', 'Paradero de prueba en Los Naranjos', 4
    UNION ALL SELECT 'DEMO-12', 'Centro Comercial Campanario', 'Paradero de prueba en Campanario', 5
    UNION ALL SELECT 'DEMO-13', 'Piendamó', 'Paradero de prueba en Piendamó', 1
    UNION ALL SELECT 'DEMO-13', 'Santa Teresa', 'Paradero de prueba en Santa Teresa', 2
    UNION ALL SELECT 'DEMO-13', 'Centro', 'Paradero de prueba en el Centro', 3
    UNION ALL SELECT 'DEMO-13', 'Terminal de Transportes', 'Paradero de prueba en la Terminal', 4
    UNION ALL SELECT 'DEMO-14', 'La Paz', 'Paradero de prueba en La Paz', 1
    UNION ALL SELECT 'DEMO-14', 'Los Naranjos', 'Paradero de prueba en Los Naranjos', 2
    UNION ALL SELECT 'DEMO-14', 'Centro', 'Paradero de prueba en el Centro', 3
    UNION ALL SELECT 'DEMO-14', 'Hospital Universitario San José', 'Paradero de prueba en el Hospital San José', 4
) AS demo
    ON r.code = CONCAT('RUTA-', LPAD(CAST(SUBSTRING(demo.code, 6) AS UNSIGNED) + 10, 2, '0'))
WHERE NOT EXISTS (
    SELECT 1
    FROM stops existing
    WHERE existing.route_id = r.id
      AND existing.name = demo.name
      AND existing.stop_order = demo.stop_order
);

INSERT INTO stops (route_id, name, landmark_reference, stop_order)
SELECT r.id, expanded.name, expanded.landmark_reference, expanded.stop_order
FROM routes r
JOIN (
    SELECT 'RUTA-11' AS code, 'Bello Horizonte' AS name, 'Sector de referencia: Bello Horizonte (recorrido simulado)' AS landmark_reference, 6 AS stop_order
    UNION ALL SELECT 'RUTA-11', 'El Uvo', 'Sector de referencia: El Uvo (recorrido simulado)', 7
    UNION ALL SELECT 'RUTA-11', 'Villa del Viento', 'Sector de referencia: Villa del Viento (recorrido simulado)', 8
    UNION ALL SELECT 'RUTA-11', 'Prados del Norte', 'Sector de referencia: Prados del Norte (recorrido simulado)', 9
    UNION ALL SELECT 'RUTA-11', 'La Florida', 'Sector de referencia: La Florida (recorrido simulado)', 10
    UNION ALL SELECT 'RUTA-12', 'Santa Clara', 'Sector de referencia: Santa Clara (recorrido simulado)', 6
    UNION ALL SELECT 'RUTA-12', 'La Aldea', 'Sector de referencia: La Aldea (recorrido simulado)', 7
    UNION ALL SELECT 'RUTA-12', 'Los Hoyos', 'Sector de referencia: Los Hoyos (recorrido simulado)', 8
    UNION ALL SELECT 'RUTA-12', 'Bello Horizonte', 'Sector de referencia: Bello Horizonte (recorrido simulado)', 9
    UNION ALL SELECT 'RUTA-12', 'La Cabaña', 'Sector de referencia: La Cabaña (recorrido simulado)', 10
    UNION ALL SELECT 'RUTA-13', 'Cadillal', 'Sector de referencia: Cadillal (recorrido simulado)', 4
    UNION ALL SELECT 'RUTA-13', 'Valencia', 'Sector de referencia: Valencia (recorrido simulado)', 5
    UNION ALL SELECT 'RUTA-13', 'El Empedrado', 'Sector de referencia: El Empedrado (recorrido simulado)', 6
    UNION ALL SELECT 'RUTA-13', 'Bolívar', 'Sector de referencia: Bolívar (recorrido simulado)', 7
    UNION ALL SELECT 'RUTA-13', 'La Pamba', 'Sector de referencia: La Pamba (recorrido simulado)', 8
    UNION ALL SELECT 'RUTA-13', 'Bloques de Pubenza', 'Sector de referencia: Bloques de Pubenza (recorrido simulado)', 9
    UNION ALL SELECT 'RUTA-13', 'San Antonio', 'Sector de referencia: San Antonio (recorrido simulado)', 10
    UNION ALL SELECT 'RUTA-14', 'Pandiguando', 'Sector de referencia: Pandiguando (recorrido simulado)', 5
    UNION ALL SELECT 'RUTA-14', 'Retiro Bajo', 'Sector de referencia: Retiro Bajo (recorrido simulado)', 6
    UNION ALL SELECT 'RUTA-14', 'San José', 'Sector de referencia: San José (recorrido simulado)', 7
    UNION ALL SELECT 'RUTA-14', 'La Sombrilla', 'Sector de referencia: La Sombrilla (recorrido simulado)', 8
    UNION ALL SELECT 'RUTA-14', 'Las Ferias', 'Sector de referencia: Las Ferias (recorrido simulado)', 9
    UNION ALL SELECT 'RUTA-14', 'La Unión', 'Sector de referencia: La Unión (recorrido simulado)', 10
    UNION ALL SELECT 'RUTA-15', 'Puelenje', 'Sector de referencia: Puelenje (recorrido simulado)', 6
    UNION ALL SELECT 'RUTA-15', 'Calicanto', 'Sector de referencia: Calicanto (recorrido simulado)', 7
    UNION ALL SELECT 'RUTA-15', 'El Pajonal', 'Sector de referencia: El Pajonal (recorrido simulado)', 8
    UNION ALL SELECT 'RUTA-15', 'Alfonso López', 'Sector de referencia: Alfonso López (recorrido simulado)', 9
    UNION ALL SELECT 'RUTA-15', 'San Bernardino', 'Sector de referencia: San Bernardino (recorrido simulado)', 10
    UNION ALL SELECT 'RUTA-15', 'Las Tres Margaritas', 'Sector de referencia: Las Tres Margaritas (recorrido simulado)', 11
    UNION ALL SELECT 'RUTA-16', 'San Camilo', 'Sector de referencia: San Camilo (recorrido simulado)', 5
    UNION ALL SELECT 'RUTA-16', 'San Rafael', 'Sector de referencia: San Rafael (recorrido simulado)', 6
    UNION ALL SELECT 'RUTA-16', 'La Estancia', 'Sector de referencia: La Estancia (recorrido simulado)', 7
    UNION ALL SELECT 'RUTA-16', 'La Ladera', 'Sector de referencia: La Ladera (recorrido simulado)', 8
    UNION ALL SELECT 'RUTA-16', 'El Mirador', 'Sector de referencia: El Mirador (recorrido simulado)', 9
    UNION ALL SELECT 'RUTA-16', 'Villa Occidente', 'Sector de referencia: Villa Occidente (recorrido simulado)', 10
    UNION ALL SELECT 'RUTA-17', 'Yanaconas', 'Sector de referencia: Yanaconas (recorrido simulado)', 4
    UNION ALL SELECT 'RUTA-17', 'Pomona', 'Sector de referencia: Pomona (recorrido simulado)', 5
    UNION ALL SELECT 'RUTA-17', 'Ciudad Jardín', 'Sector de referencia: Ciudad Jardín (recorrido simulado)', 6
    UNION ALL SELECT 'RUTA-17', 'El Recuerdo', 'Sector de referencia: El Recuerdo (recorrido simulado)', 7
    UNION ALL SELECT 'RUTA-17', 'Santa Inés', 'Sector de referencia: Santa Inés (recorrido simulado)', 8
    UNION ALL SELECT 'RUTA-17', 'El Pinar', 'Sector de referencia: El Pinar (recorrido simulado)', 9
    UNION ALL SELECT 'RUTA-17', 'Santa Helena', 'Sector de referencia: Santa Helena (recorrido simulado)', 10
    UNION ALL SELECT 'RUTA-18', 'La María Occidente', 'Sector de referencia: La María Occidente (recorrido simulado)', 5
    UNION ALL SELECT 'RUTA-18', 'Los Campos', 'Sector de referencia: Los Campos (recorrido simulado)', 6
    UNION ALL SELECT 'RUTA-18', 'Las Américas', 'Sector de referencia: Las Américas (recorrido simulado)', 7
    UNION ALL SELECT 'RUTA-18', 'La Floresta', 'Sector de referencia: La Floresta (recorrido simulado)', 8
    UNION ALL SELECT 'RUTA-18', '31 de Marzo', 'Sector de referencia: 31 de Marzo (recorrido simulado)', 9
    UNION ALL SELECT 'RUTA-18', 'Los Tejares', 'Sector de referencia: Los Tejares (recorrido simulado)', 10
    UNION ALL SELECT 'RUTA-19', 'Morinda', 'Sector de referencia: Morinda (recorrido simulado)', 4
    UNION ALL SELECT 'RUTA-19', 'Bellavista', 'Sector de referencia: Bellavista (recorrido simulado)', 5
    UNION ALL SELECT 'RUTA-19', 'La Paz', 'Sector de referencia: La Paz (recorrido simulado)', 6
    UNION ALL SELECT 'RUTA-19', 'Santa Bárbara', 'Sector de referencia: Santa Bárbara (recorrido simulado)', 7
    UNION ALL SELECT 'RUTA-19', 'La Aldea', 'Sector de referencia: La Aldea (recorrido simulado)', 8
    UNION ALL SELECT 'RUTA-19', 'La Arboleda', 'Sector de referencia: La Arboleda (recorrido simulado)', 9
    UNION ALL SELECT 'RUTA-19', 'Campo Bello', 'Sector de referencia: Campo Bello (recorrido simulado)', 10
    UNION ALL SELECT 'RUTA-20', 'Los Sauces', 'Sector de referencia: Los Sauces (recorrido simulado)', 5
    UNION ALL SELECT 'RUTA-20', 'Camilo Torres', 'Sector de referencia: Camilo Torres (recorrido simulado)', 6
    UNION ALL SELECT 'RUTA-20', 'Las Vegas', 'Sector de referencia: Las Vegas (recorrido simulado)', 7
    UNION ALL SELECT 'RUTA-20', 'Villa García', 'Sector de referencia: Villa García (recorrido simulado)', 8
    UNION ALL SELECT 'RUTA-20', 'El Retiro', 'Sector de referencia: El Retiro (recorrido simulado)', 9
    UNION ALL SELECT 'RUTA-20', 'La Capitana', 'Sector de referencia: La Capitana (recorrido simulado)', 10
    UNION ALL SELECT 'RUTA-21', 'La Aldea', 'Sector de referencia: La Aldea (recorrido simulado)', 5
    UNION ALL SELECT 'RUTA-21', 'Los Hoyos', 'Sector de referencia: Los Hoyos (recorrido simulado)', 6
    UNION ALL SELECT 'RUTA-21', 'San Fernando', 'Sector de referencia: San Fernando (recorrido simulado)', 7
    UNION ALL SELECT 'RUTA-21', 'Villa del Carmen', 'Sector de referencia: Villa del Carmen (recorrido simulado)', 8
    UNION ALL SELECT 'RUTA-21', 'Bello Horizonte', 'Sector de referencia: Bello Horizonte (recorrido simulado)', 4
    UNION ALL SELECT 'RUTA-21', 'Alto Cauca', 'Sector de referencia: Alto Cauca (recorrido simulado)', 9
    UNION ALL SELECT 'RUTA-21', 'Los Comuneros', 'Sector de referencia: Los Comuneros (recorrido simulado)', 10
    UNION ALL SELECT 'RUTA-22', 'Las Guacas', 'Sector de referencia: Las Guacas (recorrido simulado)', 6
    UNION ALL SELECT 'RUTA-22', 'Puelenje', 'Sector de referencia: Puelenje (recorrido simulado)', 7
    UNION ALL SELECT 'RUTA-22', 'María Oriente', 'Sector de referencia: María Oriente (recorrido simulado)', 8
    UNION ALL SELECT 'RUTA-22', 'Avelino Ull', 'Sector de referencia: Avelino Ull (recorrido simulado)', 9
    UNION ALL SELECT 'RUTA-22', 'Vereda Pisojé', 'Sector de referencia: Vereda Pisojé (recorrido simulado)', 10
    UNION ALL SELECT 'RUTA-22', 'Las Tres Margaritas', 'Sector de referencia: Las Tres Margaritas (recorrido simulado)', 11
    UNION ALL SELECT 'RUTA-23', 'La Rejoya', 'Sector de referencia: La Rejoya (recorrido simulado)', 5
    UNION ALL SELECT 'RUTA-23', 'El Tablazo', 'Sector de referencia: El Tablazo (recorrido simulado)', 6
    UNION ALL SELECT 'RUTA-23', 'El Placer', 'Sector de referencia: El Placer (recorrido simulado)', 7
    UNION ALL SELECT 'RUTA-23', 'Quintana', 'Sector de referencia: Quintana (recorrido simulado)', 8
    UNION ALL SELECT 'RUTA-23', 'Santa Bárbara', 'Sector de referencia: Santa Bárbara (recorrido simulado)', 9
    UNION ALL SELECT 'RUTA-23', 'La Cabaña', 'Sector de referencia: La Cabaña (recorrido simulado)', 10
    UNION ALL SELECT 'RUTA-24', 'Santa Inés', 'Sector de referencia: Santa Inés (recorrido simulado)', 5
    UNION ALL SELECT 'RUTA-24', 'La Floresta', 'Sector de referencia: La Floresta (recorrido simulado)', 6
    UNION ALL SELECT 'RUTA-24', 'Los Comuneros', 'Sector de referencia: Los Comuneros (recorrido simulado)', 7
    UNION ALL SELECT 'RUTA-24', 'El Dean', 'Sector de referencia: El Dean (recorrido simulado)', 8
    UNION ALL SELECT 'RUTA-24', 'Villa del Norte', 'Sector de referencia: Villa del Norte (recorrido simulado)', 9
    UNION ALL SELECT 'RUTA-24', 'La Estancia', 'Sector de referencia: La Estancia (recorrido simulado)', 10
) AS expanded ON expanded.code = r.code
WHERE NOT EXISTS (
    SELECT 1
    FROM stops existing
    WHERE existing.route_id = r.id
      AND existing.name = expanded.name
      AND existing.stop_order = expanded.stop_order
);

UPDATE stops s
JOIN routes r ON r.id = s.route_id
SET s.landmark_reference = CONCAT('Sector de referencia: ', s.name, ' (recorrido simulado)')
WHERE r.code BETWEEN 'RUTA-11' AND 'RUTA-24'
  AND s.landmark_reference LIKE 'Paradero de prueba%';

-- Despachos de prueba (con soporte de fecha y hora completa)
INSERT INTO dispatches (route_id, bus_plate, departure_time, status) VALUES
(1, 'TPK-102', '2026-09-02 06:30:00', 'EN_RUTA'),
(3, 'SOT-451', '2026-09-02 07:00:00', 'FINALIZADO'),
(6, 'TPB-890', '2026-09-02 07:15:00', 'EN_RUTA');

-- Incidentes viales de prueba
INSERT INTO incidents (route_id, incident_type, description, reported_by, status) VALUES
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

-- TABLA users (Soporte adicional con rol y API Key)
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL DEFAULT 'Usuario del Sistema',
    role VARCHAR(50) NOT NULL DEFAULT 'USUARIO',
    api_key VARCHAR(100) NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- 7. TABLA service_ratings (Calificaciones de calidad y satisfacción del usuario)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS service_ratings (
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
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- 8. TABLA bus_telemetry (Telemetría de pasajeros, velocidad y sobrecupo)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS bus_telemetry (
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
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- 9. TABLA emergency_alerts (Novedades críticas, botón de pánico y seguridad)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS emergency_alerts (
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
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
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

INSERT INTO users (id, username, password_hash, full_name, role, api_key) VALUES
(1, 'admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Administrador del Sistema Popayán', 'ADMIN', 'popayan-admin-key-2026'),
(2, 'operador_popayan', '1725165c9a0b3698a3d01016e0d8205155820b8d7f21835ca64c0f81c728d880', 'Carlos Meneses - Despachos Popayán', 'OPERADOR', 'popayan-operador-key-2026'),
(3, 'conductor_sotracauca', 'c4e047f954c38b86855c1c4ccea7a803f6ccec690954f68731021950bd29c0a7', 'Jairo Ordóñez - Conductor Colectivo', 'CONDUCTOR', 'popayan-conductor-key-2026'),
(4, 'ciudadano_cauca', 'c463ff27738fa30cd49b8546661c9c652f8c14272a35eb8869698198be53ed96', 'María Fernanda López - Usuaria', 'PASAJERO', 'popayan-pasajero-key-2026')
ON DUPLICATE KEY UPDATE username=VALUES(username);

-- Evaluaciones de calidad de prueba
INSERT INTO service_ratings (route_id, company, user_id, punctuality_score, comfort_score, driver_score, safety_score, final_score, category, comment) VALUES
(1, 'Sotracauca', 4, 4, 4, 5, 5, 91.00, 'EXCELENTE', 'Muy buen recorrido hacia la variante norte, bus limpio.'),
(1, 'Sotracauca', 4, 4, 3, 4, 4, 76.50, 'BUENO', 'Cumplió los tiempos en el Barrio Bolívar.'),
(2, 'Transpubenza', 4, 3, 3, 2, 3, 52.00, 'REGULAR_PLAN_MEJORA', 'El conductor manejaba con afán cerca al Centro Histórico.'),
(3, 'Translibertad', 4, 5, 4, 4, 5, 89.00, 'EXCELENTE', 'Excelente servicio hacia el Hospital San José.'),
(5, 'Translibertad', 4, 2, 2, 2, 2, 35.00, 'CRITICO_SANCIONABLE', 'Mucha demora en Calle 5 y exceso de ruido.');

-- Telemetría de aforo y sobrecupo de prueba
INSERT INTO bus_telemetry (route_id, bus_plate, current_passengers, max_capacity, occupancy_ratio, current_speed, risk_level, reinforcement_needed) VALUES
(1, 'TPK-102', 17, 19, 0.89, 32.5, 'PRECAUCION', 0),
(1, 'TPK-102', 23, 19, 1.21, 46.0, 'INFRACCION_GRAVE_ALTO_RIESGO', 1),
(3, 'SOT-451', 12, 19, 0.63, 28.0, 'NORMAL', 0),
(6, 'TPB-890', 21, 19, 1.11, 35.0, 'SOBRECUPO_CRITICO', 1);

-- Alertas de emergencia de prueba
INSERT INTO emergency_alerts (route_id, bus_plate, alert_type, severity_level, criticality_score, max_response_time_minutes, location_landmark, description, status) VALUES
(1, 'TPK-102', 'BOTON_PANICO', 'ALTA', 86.25, 9, 'Barrio Bolívar', 'Alerta silenciosa activada por riña en paradero comercial.', 'ACTIVA'),
(2, 'TPB-111', 'ACCIDENTE_VIAL', 'CRITICA', 97.50, 7, 'Parque Caldas - Centro', 'Colisión leve con motocicleta en Carrera 7, paso cerrado.', 'ACTIVA'),
(3, 'SOT-451', 'FALLA_MECANICA', 'MEDIA', 47.50, 28, 'Bello Horizonte', 'Recalentamiento del motor en subida, pasajeros transbordados.', 'RESUELTA');
