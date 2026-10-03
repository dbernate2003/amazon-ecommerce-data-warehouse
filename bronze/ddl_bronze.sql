-- =====================================================================
-- CAPA BRONCE — dato crudo del recorte 2012-01-01 a 2013-03-04
-- Todo como TEXT, tal como viene de all.txt.gz. No se modifica nunca.
-- Motor: PostgreSQL
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS bronze;

CREATE TABLE IF NOT EXISTS bronze.resenas_raw (
    id_carga        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id      TEXT,
    product_title   TEXT,
    product_price   TEXT,
    user_id         TEXT,
    profile_name    TEXT,
    helpfulness     TEXT,
    score           TEXT,
    review_time     TEXT,
    summary         TEXT,
    review_text     TEXT,
    archivo_origen  TEXT        NOT NULL DEFAULT 'all.txt.gz',
    fecha_ingesta   TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE bronze.resenas_raw IS
    'Reseñas de Amazon (SNAP) con review/time >= 1325376000 (desde 2012-01-01 UTC), sin transformar';
