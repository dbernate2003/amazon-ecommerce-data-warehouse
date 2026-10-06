-- =====================================================================
-- CAPA BRONCE — dato crudo de la historia de 3 años
-- Alcance: review/time >= 1267660800 (2010-03-04 a 2013-03-04, UTC)
-- Fuente:  all_3y.txt.gz (reducido de all.txt.gz de SNAP, 34.686.770 reseñas)
-- Filas:   9.707.634
-- Motor:   PostgreSQL 18 · base dws_amazon
--
-- En la base, la capa Bronce es la tabla raw.reviews:
--   - 10 columnas, una por campo del archivo, sin limpiar ni transformar.
--   - Todo es TEXT excepto review_time, que es BIGINT (epoch en segundos, UTC).
--   - La conversión de review_time a fecha se hace en Plata, siempre en UTC.
--   - No se modifica nunca. Para recargar: TRUNCATE (paso 4) y volver a cargar.
--
-- Guía paso a paso (descarga, conversión y carga):
--   docs/datos/guia_cargar_dws_amazon_local.md
-- =====================================================================


-- =====================================================================
-- PASO 1: Esquema y tabla (pgAdmin, Query Tool sobre dws_amazon)
-- =====================================================================
CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.reviews (
    product_id    TEXT,      -- product/productId
    title         TEXT,      -- product/title
    price         TEXT,      -- product/price: 'unknown' en muchos casos
    user_id       TEXT,      -- review/userId: 'unknown' = reseña anónima
    profile_name  TEXT,      -- review/profileName
    helpfulness   TEXT,      -- review/helpfulness: formato '3/5'
    score         TEXT,      -- review/score: formato '5.0'
    review_time   BIGINT,    -- review/time: epoch en segundos, UTC
    summary       TEXT,      -- review/summary
    review_text   TEXT       -- review/text
);

COMMENT ON TABLE raw.reviews IS
    'Capa Bronce: reseñas de Amazon (SNAP) con review/time >= 1267660800 (2010-03-04 a 2013-03-04 UTC), sin transformar';


-- =====================================================================
-- PASO 2: Verificar la estructura (antes de cargar)
-- Deben salir 10 filas: review_time = bigint y las demás = text.
-- =====================================================================
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'raw' AND table_name = 'reviews'
ORDER BY ordinal_position;

-- Debe dar 0 antes de cargar
SELECT count(*) FROM raw.reviews;


-- =====================================================================
-- PASO 3: Carga (se ejecuta en Git Bash, NO en pgAdmin)
-- \copy es un comando de psql: pgAdmin no lo reconoce.
-- Archivo de entrada: all_3y_pipe.txt (paso 3 de la guía), una reseña
-- por línea, 10 campos separados por '|', con '\' y '|' escapados.
--
--   PSQL="/c/Program Files/PostgreSQL/18/bin/psql.exe"
--   TXTW=$(cygpath -m ~/Downloads/all_3y_pipe.txt)
--   "$PSQL" -U postgres -d dws_amazon -c "\copy raw.reviews FROM '$TXTW' WITH (FORMAT text, DELIMITER '|', ENCODING 'UTF8')"
--
-- Resultado obtenido: COPY 9707634  ✔
-- La carga es atómica: si falla, no queda ninguna fila cargada.
-- =====================================================================


-- =====================================================================
-- PASO 4: Recarga (solo si hay que cargar de nuevo desde cero)
-- Vacía la tabla sin borrar su estructura. Está comentado para que
-- no se ejecute por accidente al correr todo el script.
-- =====================================================================
-- TRUNCATE raw.reviews;


-- =====================================================================
-- PASO 5: Controles de la carga
-- Resultado obtenido el 2026-10-03:
--   total_filas = 9.707.634  (igual al COPY y al archivo)  ✔
--   epoch_min   = 1267660800 -> 2010-03-04 00:00:00 UTC   ✔
--   epoch_max   = 1362355200 -> 2013-03-04 00:00:00 UTC   ✔
-- Sin AT TIME ZONE 'UTC', pgAdmin muestra la hora de Colombia
-- (2010-03-03 19:00:00-05), que es el mismo instante.
-- =====================================================================
SELECT
    COUNT(*)                                          AS total_filas,
    MIN(review_time)                                  AS epoch_min,
    MAX(review_time)                                  AS epoch_max,
    to_timestamp(MIN(review_time)) AT TIME ZONE 'UTC' AS desde_utc,
    to_timestamp(MAX(review_time)) AT TIME ZONE 'UTC' AS hasta_utc
FRO