-- Tabla para almacenar los problemas de programación lineal
CREATE TABLE problemaPL (
    problemaID TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-a' || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
    titulo TEXT NOT NULL,
    descripcion TEXT,
    tipoOptimizacion TEXT NOT NULL CHECK(tipoOptimizacion IN ('MAX', 'MIN')),
    funcionObjetivo TEXT,
    metodo TEXT NOT NULL,
    fechaCreacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para almacenar las variables asociadas a un problema
CREATE TABLE variables (
    variableID TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-a' || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
    variable TEXT NOT NULL,
    nombre TEXT,
    problemaID TEXT NOT NULL,
    fechaCreacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (problemaID) REFERENCES problemaPL(problemaID) ON DELETE CASCADE
);

-- Tabla para almacenar los métodos gráficos
CREATE TABLE metodoGrafico (
    metodoGraficoID TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-a' || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
    problemaID TEXT NOT NULL,
    valoresFO TEXT,
    mensaje TEXT,
    grafico BLOB,
    fechaCreacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (problemaID) REFERENCES problemaPL(problemaID) ON DELETE CASCADE
);

-- Tabla para almacenar los métodos simples
CREATE TABLE metodoSimple (
    metodoSimpleID TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-a' || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
    problemaID TEXT NOT NULL,
    valorFo TEXT,
    mensaje TEXT,
    fechaCreacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (problemaID) REFERENCES problemaPL(problemaID) ON DELETE CASCADE
);

CREATE TABLE iteracionSimple (
    iteracionID INTEGER PRIMARY KEY AUTOINCREMENT,
    metodoSimpleID TEXT NOT NULL,
    iteracion INT NOT NULL,
    entra TEXT,
    sale TEXT,
    razonMinima REAL,
    elementoPivote REAL,
    tabla TEXT,
    fechaCreacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (metodoSimpleID) REFERENCES metodoSimple(metodoSimpleID) ON DELETE CASCADE
);

-- Tabla para almacenar las restricciones
CREATE TABLE restricciones (
    restriccionID TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-a' || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
    problemaID TEXT NOT NULL,
    inecuacion  TEXT NOT NULL,
    glosa TEXT,
    fechaCreacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (problemaID) REFERENCES problemaPL(problemaID) ON DELETE CASCADE
);