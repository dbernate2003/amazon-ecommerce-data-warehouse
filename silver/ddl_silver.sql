-- =====================================================================
-- CAPA PLATA — modelo relacional normalizado (3FN), limpio y tipado
-- Explicación del diseño: docs/modelado/02_modelo_relacional.md
-- Motor: PostgreSQL
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS silver;

-- Un producto: título y precio dependen solo de producto_id
CREATE TABLE IF NOT EXISTS silver.producto (
    producto_id     CHAR(10)        PRIMARY KEY,           -- ASIN o ISBN-10
    titulo          TEXT            NOT NULL,              -- R09: sin entidades HTML
    precio          NUMERIC(10, 2),                        -- R04: NULL si "unknown"
    tipo_producto   VARCHAR(10)     NOT NULL,              -- R12: 'Libro' u 'Otro'
    CONSTRAINT ck_producto_precio CHECK (precio IS NULL OR precio >= 0),
    CONSTRAINT ck_producto_tipo   CHECK (tipo_producto IN ('Libro', 'Otro'))
);

-- Un cliente identificado (los anónimos no crean fila: R05)
CREATE TABLE IF NOT EXISTS silver.cliente (
    cliente_id      VARCHAR(50)     PRIMARY KEY,
    nombre_perfil   VARCHAR(100)                           -- el más reciente
);

-- Una reseña: la entidad central que relaciona producto y cliente
CREATE TABLE IF NOT EXISTS silver.resena (
    resena_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- clave sustituta
    producto_id     CHAR(10)        NOT NULL REFERENCES silver.producto (producto_id),
    cliente_id      VARCHAR(50)     REFERENCES silver.cliente (cliente_id),  -- NULL = anónima
    fecha           DATE            NOT NULL,              -- R03: Unix -> DATE (UTC)
    puntaje         SMALLINT        NOT NULL,              -- R08
    votos_utiles    INTEGER         NOT NULL,              -- R06
    votos_totales   INTEGER         NOT NULL,              -- R06
    resumen         TEXT,                                  -- R09
    texto           TEXT,                                  -- R09
    id_carga_bronce BIGINT          NOT NULL,              -- linaje hacia bronze.resenas_raw
    CONSTRAINT ck_resena_puntaje CHECK (puntaje BETWEEN 1 AND 5),
    CONSTRAINT ck_resena_votos   CHECK (votos_utiles >= 0 AND votos_utiles <= votos_totales),  -- R07
    CONSTRAINT ck_resena_fecha   CHECK (fecha >= DATE '2012-01-01'),                          -- R02
    CONSTRAINT uq_resena_natural UNIQUE (producto_id, cliente_id, fecha)                      -- R11
);

CREATE INDEX IF NOT EXISTS ix_resena_producto ON silver.resena (producto_id);
CREATE INDEX IF NOT EXISTS ix_resena_cliente  ON silver.resena (cliente_id);
CREATE INDEX IF NOT EXISTS ix_resena_fecha    ON silver.resena (fecha);
