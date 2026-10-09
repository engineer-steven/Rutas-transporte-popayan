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
    codigo VARCHAR(50) NOT NULL UNIQUE,
    empresa VARCHAR(100) NOT NULL,
    origen VARCHAR(150) NOT NULL,
    destino VARCHAR(150) NOT NULL,
    tarifa DECIMAL(10,2) NOT NULL DEFAULT 2800.00,
    horario VARCHAR(100) NOT NULL DEFAULT '05:30 - 21:00',
    estado VARCHAR(50) NOT NULL DEFAULT 'ACTIVA'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. TABLA paraderos (Paraderos y puntos de referencia de cada ruta)
CREATE TABLE IF NOT EXISTS paraderos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ruta_id INT NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    referencia VARCHAR(200),
    orden INT NOT NULL,
    FOREIGN KEY (ruta_id) REFERENCES rutas(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. TABLA despachos (Control de despachos e intervalos entre buses)
CREATE TABLE IF NOT EXISTS despachos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ruta_id INT NOT NULL,
    placa_bus VARCHAR(20) NOT NULL,
    hora_salida DATETIME NOT NULL,
    estado VARCHAR(50) NOT NULL DEFAULT 'EN_RUTA',
    FOREIGN KEY (ruta_id) REFERENCES rutas(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. TABLA incidentes (Reporte de novedades viales, tráfico y desvíos)
CREATE TABLE IF NOT EXISTS incidentes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ruta_id INT NOT NULL,
    tipo_incidente VARCHAR(50) NOT NULL,
    descripcion TEXT NOT NULL,
    reportado_por VARCHAR(100) NOT NULL,
    fecha_reporte DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(50) NOT NULL DEFAULT 'ACTIVO',
    FOREIGN KEY (ruta_id) REFERENCES rutas(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- 6. DATOS INICIALES DE PRUEBA (POPAYÁN) 
-- ==============================================================================

-- Rutas 
INSERT INTO rutas (id, codigo, empresa, origen, destino, tarifa, horario, estado) VALUES
(1, 'RUTA-1', 'Sotracauca', 'Barrio Bolívar', 'Campanario / Variante Norte', 2800.00, '05:30 - 21:30', 'ACTIVA'),
(2, 'LINEA-2', 'Transpubenza', 'Lomas de Granada', 'Terminal de Transportes', 2800.00, '06:00 - 21:00', 'ACTIVA'),
(3, 'RUTA-5', 'Translibertad', 'Bello Horizonte', 'Hospital San José / Centro', 2900.00, '05:45 - 20:45', 'ACTIVA'),
(4, 'RUTA-9', 'Sotracauca', 'Terminal de Transportes', 'Variante Norte / Campanario', 2800.00, '06:00 - 22:00', 'ACTIVA'),
(5, 'TL1BT', 'Translibertad', 'Calle 5', 'Calle 5', 2500.00, '05:00 - 21:30', 'ACTIVA'),
(6, 'TT1M', 'Transtambo', 'Cajete', 'Pisojé', 2500.00, '05:30 - 20:00', 'ACTIVA')
ON DUPLICATE KEY UPDATE codigo=VALUES(codigo);

-- Rutas adicionales reales de Popayán 
INSERT INTO rutas (id, codigo, empresa, origen, destino, tarifa, horario, estado) VALUES
(7,  'TP1BT', 'Transpubenza', 'La Paz', 'Los Naranjos', 2500.00, '05:30 - 21:00', 'ACTIVA'),
(8,  'TP9BT', 'Transpubenza', 'Lomas de Granada', 'La Venta', 2500.00, '05:30 - 21:00', 'ACTIVA'),
(9,  'SC1M',  'Sotracauca', 'Calle 72 Norte', 'Calle 72 Norte', 2500.00, '05:00 - 22:00', 'ACTIVA'),
(10, 'SC7M',  'Sotracauca', 'Piendamó', 'Santa Teresa', 2500.00, '05:00 - 22:00', 'ACTIVA')
ON DUPLICATE KEY UPDATE codigo=VALUES(codigo);


-- Paraderos de la Ruta 1 (Barrio Bolívar -> Campanario)
INSERT INTO paraderos (ruta_id, nombre, referencia, orden) VALUES
(1, 'Barrio Bolívar', 'Zona comercial central', 1),
(1, 'Centro', 'Parque Caldas', 2),
(1, 'Centro Comercial Campanario', 'Frente a Olímpica', 3),
(1, 'Variante Norte', 'Glorieta Chirimía norte', 4);

-- Paraderos de la Ruta 2 - LINEA-2 (Lomas de Granada -> Terminal de Transportes)
INSERT INTO paraderos (ruta_id, nombre, referencia, orden) VALUES
(2, 'Lomas de Granada', 'Entrada sector 3', 1),
(2, 'Barrio La Esmeralda', 'Frente a droguería La Economía', 2),
(2, 'Parque Caldas - Centro', 'Carrera 7 con Calle 5', 3),
(2, 'Terminal de Transportes', 'Bahía de desembarque taquillas', 4);

-- Paraderos de la Ruta 5 (Bello Horizonte -> Hospital San José)
INSERT INTO paraderos (ruta_id, nombre, referencia, orden) VALUES
(3, 'Bello Horizonte', 'Cerca a polideportivo norte', 1),
(3, 'Centro Comercial Campanario', 'Frente a Olímpica', 2),
(3, 'Hospital Universitario San José', 'Entrada consulta externa', 3);

-- Paraderos de la Ruta 9 (Terminal -> Variante Norte / Campanario)
INSERT INTO paraderos (ruta_id, nombre, referencia, orden) VALUES
(4, 'Terminal de Transportes', 'Bahía principal', 1),
(4, 'Centro Comercial Campanario', 'Entrada Panamericana', 2),
(4, 'Variante Norte', 'Glorieta Chirimía norte', 3);

-- Paraderos de la Ruta TL1BT (Calle 5, circular)
INSERT INTO paraderos (ruta_id, nombre, referencia, orden) VALUES
(5, 'Calle 5', 'Eje vial Calle 5', 1),
(5, 'Comuna 2', 'Zona norte', 2);

-- Paraderos de la Ruta TT1M (Cajete -> Pisojé)
INSERT INTO paraderos (ruta_id, nombre, referencia, orden) VALUES
(6, 'Cajete', 'Vereda Cajete', 1),
(6, 'Lomas de Granada', 'Entrada principal etapa 1', 2),
(6, 'Galería La Esmeralda', 'Terminal de buses colectivos', 3),
(6, 'Pisojé', 'Vereda Pisojé', 4);

-- Despachos de prueba
INSERT INTO despachos (ruta_id, placa_bus, hora_salida, estado) VALUES
(1, 'TPK-102', '2026-09-02 06:30:00', 'EN_RUTA'),
(3, 'SOT-451', '2026-09-02 07:00:00', 'FINALIZADO'),
(6, 'TPB-890', '2026-09-02 07:15:00', 'EN_RUTA');

-- Incidentes viales de prueba
INSERT INTO incidentes (ruta_id, tipo_incidente, descripcion, reportado_por, estado) VALUES
(1, 'CONGESTION', 'Tráfico pesado en el sector del centro histórico por obras viales.', 'Conductor', 'ACTIVO'),
(3, 'DESVIO', 'Cierre temporal de vía cerca al puente por manifestación.', 'Pasajero', 'RESUELTO');
