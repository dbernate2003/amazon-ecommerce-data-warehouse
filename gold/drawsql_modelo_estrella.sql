CREATE TABLE "dim_producto"(
    "producto_sk" INTEGER NOT NULL,
    "producto_id" VARCHAR(20) NOT NULL,
    "titulo" VARCHAR(500) NOT NULL,
    "tipo_producto" VARCHAR(20) NOT NULL,
    "precio" DECIMAL(10, 2) NULL,
    "rango_precio" VARCHAR(20) NOT NULL,
    "tiene_precio" BOOLEAN NOT NULL,
    "fecha_carga" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL
);
ALTER TABLE "dim_producto" ADD PRIMARY KEY("producto_sk");
ALTER TABLE "dim_producto" ADD CONSTRAINT "dim_producto_producto_id_unique" UNIQUE("producto_id");

CREATE TABLE "dim_cliente"(
    "cliente_sk" INTEGER NOT NULL,
    "cliente_id" VARCHAR(50) NOT NULL,
    "nombre_perfil" VARCHAR(100) NOT NULL,
    "es_anonimo" BOOLEAN NOT NULL,
    "fecha_carga" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL
);
ALTER TABLE "dim_cliente" ADD PRIMARY KEY("cliente_sk");
ALTER TABLE "dim_cliente" ADD CONSTRAINT "dim_cliente_cliente_id_unique" UNIQUE("cliente_id");

CREATE TABLE "dim_fecha"(
    "fecha_sk" INTEGER NOT NULL,
    "fecha" DATE NOT NULL,
    "anio" SMALLINT NOT NULL,
    "semestre" SMALLINT NOT NULL,
    "trimestre" SMALLINT NOT NULL,
    "mes" SMALLINT NOT NULL,
    "nombre_mes" VARCHAR(15) NOT NULL,
    "anio_mes" CHAR(7) NOT NULL,
    "dia" SMALLINT NOT NULL,
    "dia_semana" SMALLINT NOT NULL,
    "nombre_dia" VARCHAR(15) NOT NULL,
    "es_fin_semana" BOOLEAN NOT NULL
);
ALTER TABLE "dim_fecha" ADD PRIMARY KEY("fecha_sk");
ALTER TABLE "dim_fecha" ADD CONSTRAINT "dim_fecha_fecha_unique" UNIQUE("fecha");

CREATE TABLE "dim_calificacion"(
    "calificacion_sk" SMALLINT NOT NULL,
    "estrellas" SMALLINT NULL,
    "descripcion" VARCHAR(20) NOT NULL,
    "sentimiento" VARCHAR(15) NOT NULL
);
ALTER TABLE "dim_calificacion" ADD PRIMARY KEY("calificacion_sk");

CREATE TABLE "dim_utilidad"(
    "utilidad_sk" SMALLINT NOT NULL,
    "rango_utilidad" VARCHAR(30) NOT NULL,
    "porcentaje_min" DECIMAL(5, 2) NULL,
    "porcentaje_max" DECIMAL(5, 2) NULL
);
ALTER TABLE "dim_utilidad" ADD PRIMARY KEY("utilidad_sk");

CREATE TABLE "fact_resenas"(
    "resena_id" BIGINT NOT NULL,
    "producto_sk" INTEGER NOT NULL,
    "cliente_sk" INTEGER NOT NULL,
    "fecha_sk" INTEGER NOT NULL,
    "calificacion_sk" SMALLINT NOT NULL,
    "utilidad_sk" SMALLINT NOT NULL,
    "cantidad_resenas" SMALLINT NOT NULL,
    "puntaje" SMALLINT NULL,
    "votos_utiles" INTEGER NOT NULL,
    "votos_totales" INTEGER NOT NULL,
    "longitud_texto" INTEGER NOT NULL,
    "fecha_carga" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL
);
ALTER TABLE "fact_resenas" ADD PRIMARY KEY("resena_id");
ALTER TABLE "fact_resenas" ADD CONSTRAINT "fact_resenas_producto_sk_foreign" FOREIGN KEY("producto_sk") REFERENCES "dim_producto"("producto_sk");
ALTER TABLE "fact_resenas" ADD CONSTRAINT "fact_resenas_cliente_sk_foreign" FOREIGN KEY("cliente_sk") REFERENCES "dim_cliente"("cliente_sk");
ALTER TABLE "fact_resenas" ADD CONSTRAINT "fact_resenas_fecha_sk_foreign" FOREIGN KEY("fecha_sk") REFERENCES "dim_fecha"("fecha_sk");
ALTER TABLE "fact_resenas" ADD CONSTRAINT "fact_resenas_calificacion_sk_foreign" FOREIGN KEY("calificacion_sk") REFERENCES "dim_calificacion"("calificacion_sk");
ALTER TABLE "fact_resenas" ADD CONSTRAINT "fact_resenas_utilidad_sk_foreign" FOREIGN KEY("utilidad_sk") REFERENCES "dim_utilidad"("utilidad_sk");
