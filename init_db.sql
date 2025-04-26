-- Script de inicialización de la base de datos

-- Tabla de temperaturas
CREATE TABLE IF NOT EXISTS temperatures (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    temperature DECIMAL(5,2) NOT NULL,
    is_period TINYINT(1) DEFAULT 0,
    cycle_day INT NOT NULL,
    comment TEXT,
    mucus_type VARCHAR(50),
    mood VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de registros de ciclos
CREATE TABLE IF NOT EXISTS cycle_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    duration INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para el contador de días del ciclo
CREATE TABLE IF NOT EXISTS cycle_counter (
    id INT AUTO_INCREMENT PRIMARY KEY,
    day_counter INT NOT NULL DEFAULT 1,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de configuración
CREATE TABLE IF NOT EXISTS settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_name VARCHAR(50) NOT NULL,
    setting_value TEXT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insertar valores iniciales si no existen
INSERT INTO cycle_counter (day_counter) 
SELECT 1 FROM dual 
WHERE NOT EXISTS (SELECT 1 FROM cycle_counter);

-- Insertar configuraciones predeterminadas si no existen
INSERT INTO settings (setting_name, setting_value) 
SELECT 'fertile_temp', '98.6' FROM dual 
WHERE NOT EXISTS (SELECT 1 FROM settings WHERE setting_name = 'fertile_temp');

INSERT INTO settings (setting_name, setting_value) 
SELECT 'cycle_length', '28' FROM dual 
WHERE NOT EXISTS (SELECT 1 FROM settings WHERE setting_name = 'cycle_length');

INSERT INTO settings (setting_name, setting_value) 
SELECT 'temperature_unit', 'F' FROM dual 
WHERE NOT EXISTS (SELECT 1 FROM settings WHERE setting_name = 'temperature_unit'); 