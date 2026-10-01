-- =====================================================================
-- CAPA ORO — esquema estrella (Kimball): 1 tabla de hechos y 5 dimensiones
-- Grano: una fila = una reseña de un cliente sobre un producto en una fecha
-- Diseño: docs/modelado/03_modelo_estrella.md
-- Motor: PostgreSQL
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS gold;

-- ---------------------------------------------------------------------
-- DIMENSIONES
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gold.dim_producto (
    producto_sk     INTEGER         PRIMARY KEY,           -- clave subrogada
    producto_id     VARCHAR(20)     NOT NULL UNIQUE,       -- clave natural (ASIN / ISBN-10)
    titulo          VARCHAR(500)    NOT NULL,
    tipo_producto   VARCHAR(20)     NOT NULL,              -- 'Libro' | 'Otro' | 'Desconocido'
    precio          NUMERIC(10, 2),
    rango_precio    VARCHAR(20)     NOT NULL,              -- 'Sin precio' | '< $10' | '$10-$25' | '$25-$50' | '> $50'
    tiene_precio    BOOLEAN         NOT NULL,
    fecha_carga     TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gold.dim_cliente (
    cliente_sk      INTEGER         PRIMARY KEY,
    cliente_id      VARCHAR(50)     NOT NULL UNIQUE,
    nombre_perfil   VARCHAR(100)    NOT NULL,
    es_anonimo      BOOLEAN         NOT NULL,
    fecha_carga     TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gold.dim_fecha (
    fecha_sk        INTEGER         PRIMARY KEY,           -- YYYYMMDD; -1 = desconocida
    fecha           DATE            NOT NULL UNIQUE,
    anio            SMALLINT        NOT NULL,
    semestre        SMALLINT        NOT NULL,
    trimestre       SMALLINT        NOT NULL,
    mes             SMALLINT        NOT NULL,
    nombre_mes      VARCHAR(15)     NOT NULL,
    anio_mes        CHAR(7)         NOT NULL,              -- '2012-12', para series mensuales
    dia             SMALLINT        NOT NULL,
    dia_semana      SMALLINT        NOT NULL,              -- 1 = lunes ... 7 = domingo
    nombre_dia      VARCHAR(15)     NOT NULL,
    es_fin_semana   BOOLEAN         NOT NULL
);

CREATE TABLE IF NOT EXISTS gold.dim_calificacion (
    calificacion_sk SMALLINT        PRIMARY KEY,
    estrellas       SMALLINT,                              -- 1..5; NULL en la fila -1
    descripcion     VARCHAR(20)     NOT NULL,              -- '1 estrella' ... '5 estrellas'
    sentimiento     VARCHAR(15)     NOT NULL               -- 'Negativa' (1-2) | 'Neutral' (3) | 'Positiva' (4-5)
);

CREATE TABLE IF NOT EXISTS gold.dim_utilidad (
    utilidad_sk     SMALLINT        PRIMARY KEY,
    rango_utilidad  VARCHAR(30)     NOT NULL,              -- 'Sin votos' | 'Baja' | 'Media' | 'Alta'
    porcentaje_min  NUMERIC(5, 2),
    porcentaje_max  NUMERIC(5, 2)
);

-- ---------------------------------------------------------------------
-- HECHOS
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gold.fact_resenas (
    resena_id        BIGINT         PRIMARY KEY,           -- dimensión degenerada (linaje a silver.resena)
    producto_sk      INTEGER        NOT NULL REFERENCES gold.dim_producto (producto_sk),
    cliente_sk       INTEGER        NOT NULL REFERENCES gold.dim_cliente (cliente_sk),
    fecha_sk         INTEGER        NOT NULL REFERENCES gold.dim_fecha (fecha_sk),
    calificacion_sk  SMALLINT       NOT NULL REFERENCES gold.dim_calificacion (calificacion_sk),
    utilidad_sk      SMALLINT       NOT NULL REFERENCES gold.dim_utilidad (utilidad_sk),
    cantidad_resenas SMALLINT       NOT NULL DEFAULT 1,    -- aditiva
    puntaje          SMALLINT,                             -- no aditiva: se promedia
    votos_utiles     INTEGER        NOT NULL,              -- aditiva
    votos_totales    INTEGER        NOT NULL,              -- aditiva
    longitud_texto   INTEGER        NOT NULL,              -- aditiva
    fecha_carga      TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_fact_producto     ON gold.fact_resenas (producto_sk);
CREATE INDEX IF NOT EXISTS ix_fact_cliente      ON gold.fact_resenas (cliente_sk);
CREATE INDEX IF NOT EXISTS ix_fact_fecha        ON gold.fact_resenas (fecha_sk);
CREATE INDEX IF NOT EXISTS ix_fact_calificacion ON gold.fact_resenas (calificacion_sk);
CREATE INDEX IF NOT EXISTS ix_fact_utilidad     ON gold.fact_resenas (utilidad_sk);

-- ---------------------------------------------------------------------
-- FILAS ESPECIALES (miembros "Desconocido" y "Anónimo")
-- Ningún hecho queda con clave foránea NULL: si falta el dato, apunta aquí.
-- ---------------------------------------------------------------------
INSERT INTO gold.dim_producto (producto_sk, producto_id, titulo, tipo_producto, precio, rango_precio, tiene_precio)
VALUES (-1, 'N/A', 'Desconocido', 'Desconocido', NULL, 'Sin precio', FALSE)
ON CONFLICT DO NOTHING;

INSERT INTO gold.dim_cliente (cliente_sk, cliente_id, nombre_perfil, es_anonimo) VALUES
    (-1, 'N/A',     'Desconocido', FALSE),
    (-2, 'ANONIMO', 'Anónimo',     TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO gold.dim_fecha (fecha_sk, fecha, anio, semestre, trimestre, mes, nombre_mes, anio_mes, dia, dia_semana, nombre_dia, es_fin_semana)
VALUES (-1, DATE '1900-01-01', 1900, 0, 0, 0, 'Desconocido', '0000-00', 0, 0, 'Desconocido', FALSE)
ON CONFLICT DO NOTHING;

INSERT INTO gold.dim_calificacion (calificacion_sk, estrellas, descripcion, sentimiento) VALUES
    (-1, NULL, 'Desconocida', 'Desconocido'),
    ( 1, 1, '1 estrella',  'Negativa'),
    ( 2, 2, '2 estrellas', 'Negativa'),
    ( 3, 3, '3 estrellas', 'Neutral'),
    ( 4, 4, '4 estrellas', 'Positiva'),
    ( 5, 5, '5 estrellas', 'Positiva')
ON CONFLICT DO NOTHING;

INSERT INTO gold.dim_utilidad (utilidad_sk, rango_utilidad, porcentaje_min, porcentaje_max) VALUES
    (-1, 'Desconocida', NULL,  NULL),
    ( 0, 'Sin votos',   NULL,  NULL),
    ( 1, 'Baja',        0.00,  39.99),
    ( 2, 'Media',       40.00, 69.99),
    ( 3, 'Alta',        70.00, 100.00)
ON CONFLICT DO NOTHING;

-- Calendario completo 2012-2013 (731 días), generado y no extraído de la fuente
INSERT INTO gold.dim_fecha (fecha_sk, fecha, anio, semestre, trimestre, mes, nombre_mes, anio_mes, dia, dia_semana, nombre_dia, es_fin_semana)
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INTEGER,
    d::DATE,
    EXTRACT(YEAR FROM d)::SMALLINT,
    CASE WHEN EXTRACT(MONTH FROM d) <= 6 THEN 1 ELSE 2 END,
    EXTRACT(QUARTER FROM d)::SMALLINT,
    EXTRACT(MONTH FROM d)::SMALLINT,
    (ARRAY['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'])[EXTRACT(MONTH FROM d)::INT],
    TO_CHAR(d, 'YYYY-MM'),
    EXTRACT(DAY FROM d)::SMALLINT,
    EXTRACT(ISODOW FROM d)::SMALLINT,
    (ARRAY['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'])[EXTRACT(ISODOW FROM d)::INT],
    EXTRACT(ISODOW FROM d) IN (6, 7)
FROM generate_series(DATE '2012-01-01', DATE '2013-12-31', INTERVAL '1 day') AS d
ON CONFLICT DO NOTHING;
