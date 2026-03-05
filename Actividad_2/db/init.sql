-- Crear tabla de estudiantes
CREATE TABLE IF NOT EXISTS estudiantes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    carrera VARCHAR(100) NOT NULL,
    semestre INT NOT NULL
);

-- Insertar datos iniciales
INSERT INTO estudiantes (nombre, apellido, email, carrera, semestre) VALUES
('Juan', 'Perez', 'juan.perez@universidad.edu', 'Ingeniería de Sistemas', 5),
('Maria', 'Gomez', 'maria.gomez@universidad.edu', 'Derecho', 3),
('Carlos', 'Rodriguez', 'carlos.rod@universidad.edu', 'Medicina', 8),
('Ana', 'Martinez', 'ana.mtz@universidad.edu', 'Administración', 2),
('Luis', 'Torres', 'luis.torres@universidad.edu', 'Psicología', 4);
