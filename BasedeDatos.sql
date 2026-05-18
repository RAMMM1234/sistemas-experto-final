-- Base de datos: sistema_experto
-- Ejecuta este script dentro de pgAdmin o Query Tool.
-- No borra datos existentes; crea/actualiza las tablas necesarias.

CREATE TABLE IF NOT EXISTS enfermedades (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS sintomas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    enfermedad_id INT REFERENCES enfermedades(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS evaluaciones (
    id SERIAL PRIMARY KEY,
    resultado TEXT NOT NULL,
    sintomas TEXT,
    puntos INTEGER DEFAULT 0,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reparación por si la tabla evaluaciones ya existía incompleta.
ALTER TABLE evaluaciones ADD COLUMN IF NOT EXISTS sintomas TEXT;
ALTER TABLE evaluaciones ADD COLUMN IF NOT EXISTS puntos INTEGER DEFAULT 0;
ALTER TABLE evaluaciones ADD COLUMN IF NOT EXISTS fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Datos base opcionales.
INSERT INTO enfermedades (nombre, descripcion)
SELECT 'Diabetes', 'Enfermedad crónica relacionada con niveles altos de glucosa en sangre.'
WHERE NOT EXISTS (SELECT 1 FROM enfermedades WHERE nombre = 'Diabetes');

INSERT INTO sintomas (nombre, enfermedad_id)
SELECT nombre, (SELECT id FROM enfermedades WHERE nombre = 'Diabetes' LIMIT 1)
FROM (VALUES
    ('Mucha sed'),
    ('Orina frecuente'),
    ('Cansancio'),
    ('Visión borrosa'),
    ('Pérdida de peso'),
    ('Antecedentes familiares')
) AS s(nombre)
WHERE NOT EXISTS (SELECT 1 FROM sintomas WHERE sintomas.nombre = s.nombre);

SELECT * FROM evaluaciones ORDER BY fecha DESC;
