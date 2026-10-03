# Plan de la entrega: tema del proyecto y diseño del modelo estrella

Este plan aplica la guía *Diseño del Data Warehouse y Modelo Estrella* al proyecto de reseñas de Amazon. La guía usa como ejemplo un DWH de **ventas** con fuentes ERP y CRM; aquí se adapta a lo que **sí** tiene este proyecto: una sola fuente (`all.txt.gz` de SNAP), ya explorada, normalizada en la capa Plata y con un primer diseño de estrella en `03_modelo_estrella.md` y `ddl_gold.sql`.

**Qué pide esta entrega:**
1. Enfocar el proyecto en un **tema**, es decir, un proceso o área de negocio. El tema no es una dimensión.
2. **Diseñar** el modelo estrella. La implementación en SQL viene después, con el ETL.

**Regla de este plan:** toda afirmación sale de la documentación del proyecto: `00_planteamiento.md`, `01_exploracion_bd.md`, `02_modelo_relacional.md`, `03_modelo_estrella.md`, `ddl_silver.sql`, `ddl_gold.sql` y `mer_drawio.xml`. Lo que todavía no está medido aparece marcado como **pendiente**.

---

## 1. El tema: qué proceso de negocio se analiza

### 1.1 Tema propuesto

> **Área de negocio:** experiencia del cliente y reputación de productos en el comercio electrónico.
>
> **Proceso de negocio:** la publicación y valoración de reseñas de productos. Un cliente publica una reseña con una calificación de 1 a 5 sobre un producto, y la comunidad vota si esa reseña le resultó útil.
>
> **Título para el profesor:** *Análisis de la satisfacción del cliente y la reputación de productos de Amazon a partir de sus reseñas (enero 2012 – marzo 2013).*

**Sustento en la documentación:**
- El objetivo general busca "analizar la satisfacción de los clientes, la utilidad de las reseñas y el comportamiento de productos y clientes" (`00_planteamiento.md`).
- Los dos KGI son **Satisfacción del cliente** (% de reseñas de 4-5 ★) y **Confianza de la comunidad** (% de votos útiles) (`00_planteamiento.md`, sección 5).
- El paso 1 de Kimball ya identifica el proceso como "publicación de reseñas de productos en Amazon" (`03_modelo_estrella.md`).

### 1.2 Por qué este proceso y no otro

Un proceso de negocio se modela como tabla de hechos solo si la fuente registra **eventos** con **medidas**. Estos son los candidatos y lo que dicen los datos de cada uno:

| Proceso candidato | ¿La fuente lo registra? | Decisión |
|---|---|---|
| **Publicación y valoración de reseñas** | Sí. Cada registro es una reseña con fecha, producto, cliente, puntaje y votos | **Se elige** |
| Ventas (el ejemplo de la guía) | No. Ningún campo de cantidad, pedido, total ni ingreso | Descartado: no se puede copiar el `FactVentas` de la guía |
| Gestión del catálogo y precios | No es un evento. El precio es un atributo fijo de cada producto (un solo precio por producto) y falta en el 62,1 % | Queda como atributo de `dim_producto` |
| Votación de utilidad como proceso propio | No. Los votos llegan como un acumulado `a/b` dentro de cada reseña, sin fecha ni autor del voto | Los votos son **medidas de la reseña**, no un evento aparte |

Como hay **un solo proceso**, el modelo es **una estrella con una tabla de hechos**, no una constelación.

### 1.3 Plantilla de la guía (sección 24), llena para este proyecto

```text
Proceso:      Publicación y valoración de reseñas de productos
Grano:        Una fila representa una reseña publicada por un cliente
              (o de forma anónima) sobre un producto en una fecha
Dimensiones:  Producto · Cliente · Fecha · Calificación · Utilidad
Hechos:       cantidad_resenas · puntaje · votos_utiles · votos_totales · longitud_texto
```

---

## 2. Modelo relacional (Plata) frente a modelo dimensional (Oro)

En este proyecto **no hay un sistema OLTP**: la fuente es un archivo plano. El papel del "modelo operacional" de la guía lo cumple el **modelo relacional en 3FN de la capa Plata**, que se diseñó al normalizar el archivo (`02_modelo_relacional.md`, `mer_drawio.xml`).

| Aspecto | Modelo relacional · Plata | Modelo dimensional · Oro |
|---|---|---|
| Para qué existe | Guardar **una sola versión confiable** de cada dato | **Analizar**: filtrar, agrupar y medir rápido |
| Forma | Normalizado (3FN): sin redundancia | Desnormalizado (estrella): pocas uniones |
| Tablas | `producto`, `cliente`, `resena` | `fact_resenas` + 5 dimensiones |
| Claves | Naturales (`producto_id`, `cliente_id`) y sustituta en reseña | **Subrogadas** (`*_sk`) generadas por la bodega; las naturales se conservan como atributos |
| Datos faltantes | `NULL` (precio, cliente anónimo) | Filas especiales: **-1 Desconocido**, **-2 Anónimo**; ninguna FK nula |
| Texto de la reseña | Se conserva | No entra; solo `longitud_texto` |
| Atributos de análisis | No existen | Se agregan: calendario, sentimiento, rangos de precio y de utilidad |

### 2.1 De 3 tablas a 1 hecho y 5 dimensiones (no es una copia)

| En Plata | En Oro | Por qué |
|---|---|---|
| `silver.resena` (entidad que resuelve la relación M:N cliente–producto) | **`fact_resenas`**, no una dimensión | Es el **evento** que se mide: tiene fecha, medidas y conecta las demás entidades |
| `resena.resena_id` | Dimensión **degenerada** dentro del hecho | Sirve para el linaje; no tiene atributos propios (guía, sección 17) |
| `silver.producto` | `dim_producto` + `rango_precio` y `tiene_precio` | Responde **qué** se reseñó (RQ-01 a RQ-07) |
| `silver.cliente` | `dim_cliente` + filas -1 y -2 | Responde **quién** reseñó (RQ-08 a RQ-12) |
| `resena.fecha` (un atributo) | `dim_fecha`, calendario generado | Año, trimestre, mes y día de la semana (RQ-13 a RQ-16) |
| `resena.puntaje` (un atributo) | `dim_calificacion` + medida `puntaje` | Sentimiento Negativa / Neutral / Positiva (RQ-03, RQ-17, RQ-18, RQ-20) |
| `resena.votos_utiles` y `votos_totales` | `dim_utilidad` (rango) + 2 medidas | Rango de confianza (RQ-10, RQ-19, RQ-20) |
| `resena.resumen` y `texto` | **No entran** a la estrella | Pesan unos 740 bytes por fila y no se agregan; queda la medida `longitud_texto` |

**Lectura:** solo 2 de las 5 dimensiones vienen de una tabla de Plata. Las otras 3 nacen de **atributos de la reseña**, porque son ejes de análisis que piden los requerimientos.

---

## 3. La guía aplicada al proyecto: estado de los 17 pasos

| # | Paso de la guía | Estado | Evidencia | Qué falta |
|---|---|---|---|---|
| 1 | Requisitos | ✔ | 20 requerimientos, KPI y KGI (`00_planteamiento.md`) | — |
| 2 | Procesos de negocio | ◐ | Paso 1 de Kimball en `03_modelo_estrella.md` | Declararlo como **tema** con su justificación (T2-01) |
| 3 | Exploración (ERP + CRM en la guía) | ✔ | Una sola fuente, explorada completa (`01_exploracion_bd.md`) | — |
| 4 | Calidad de datos | ✔ | Reglas R01–R13 | — |
| 5 | Integración de fuentes | No aplica | Hay una sola fuente | Equivalente interno: anónimos y duplicados por productos fusionados (T2-04) |
| 6 | Volumetría | ◐ | Fuente y alcance medidos (5.627.079 reseñas, ≈ 5,8 GB) | Filas reales de producto y cliente del recorte, y tamaño de Oro (T2-03, T2-10) |
| 7 | Granularidad | ✔ | `03_modelo_estrella.md` | Comprobar la unicidad del grano (T2-04) |
| 8 | Dimensiones | ✔ | 5 dimensiones | Justificar cada una con requerimientos (T2-05) |
| 9 | Hechos | ✔ | 5 medidas | Precisar la aditividad y las fórmulas (T2-06) |
| 10 | Claves | ✔ | SK, NK, filas -1 y -2 en `ddl_gold.sql` | Tabla de linaje Plata → Oro (T2-07) |
| 11 | Tratamiento histórico | ✔ | SCD tipo 1 | Justificarlo con la guía (T2-08) |
| 12 | Relaciones | ✔ | Hecho N:1 con cada dimensión | — |
| 13 | Validar requisitos | ✔ | Matriz de bus (`03_modelo_estrella.md`, sección 6) | Pasar el checklist de la guía (T2-09) |
| 14 | Modelo físico | ✔ | `ddl_gold.sql` (tablas e índices) | Justificar tablas en lugar de vistas (T2-10) |
| 15 | Implementar Gold | Después | Corresponde a la entrega del ETL | — |
| 16 | Documentar | ◐ | `03_modelo_estrella.md` | Alinearlo con el DDL y con este plan (T2-11) |
| 17 | Diagramar en Draw.io | ◐ | MER en `mer_drawio.xml` | Estrella conceptual y lógica en draw.io (T2-12) |

✔ hecho · ◐ parcial · No aplica / Después = fuera de esta entrega

---

## 4. Decisiones de diseño que hay que sustentar

| Decisión | Qué se decidió | Por qué (evidencia) | Alternativa descartada |
|---|---|---|---|
| **Grano** | 1 fila = 1 reseña | Es el nivel más fino disponible; permite analizar por cliente y por reseña (RQ-08 a RQ-12, RQ-20) | Producto × día: perdería al cliente y la utilidad por reseña |
| **Hechos** | `cantidad_resenas`, `votos_utiles`, `votos_totales`, `longitud_texto` (aditivos); `puntaje` (se promedia) | Los porcentajes se calculan al final, nunca se suman: % útil = SUM(votos_utiles) / SUM(votos_totales) | Guardar porcentajes ya calculados en el hecho |
| **Dimensiones** | Producto, Cliente, Fecha, Calificación, Utilidad | La matriz de bus usa las 5 y cubre los 20 requerimientos | Categoría, vendedor y ubicación: la fuente no los trae |
| **Claves** | Subrogadas `*_sk`; `fecha_sk` = YYYYMMDD | Desacopla la bodega de los IDs de la fuente | Usar `producto_id` o `cliente_id` como FK |
| **Faltantes** | -1 Desconocido; -2 Anónimo; utilidad 0 "Sin votos" | El 14,5 % de las reseñas es anónimo y el 32,2 % no tiene votos | FK nula en el hecho |
| **Histórico** | SCD tipo 1 | El archivo está cerrado en marzo de 2013; la guía pide no agregar SCD tipo 2 sin necesidad (sección 16) | SCD tipo 2 |
| **Topología** | Estrella | Un solo proceso; dimensiones pequeñas frente al hecho | Copo de nieve o constelación |
| **Gold físico** | Tablas con índices en las FK | Unos 5,6 M de filas en el hecho; la guía pide justificar tablas o vistas (sección 20) | Vistas, como en el video |

**Técnicas especiales de la guía (sección 17), evaluadas una por una:**

| Técnica | ¿Se usa? | Motivo |
|---|---|---|
| Dimensión degenerada | **Sí** | `resena_id` vive en el hecho |
| Dimensión de rol (role-playing) | No | Solo hay una fecha por reseña (`review/time`) |
| Junk dimension | No | Calificación y Utilidad podrían unirse en una sola tabla de unas 30 combinaciones. Se mantienen separadas porque responden requerimientos distintos y son más claras para filtrar en Tableau |
| Hecho sin medidas (factless) | No | El evento tiene medidas |
| Bridge | No | No hay relaciones M:N dentro de una dimensión en el alcance actual |

---

## 5. Hallazgos de la revisión de arquitectura

Puntos que conviene corregir o aclarar antes de sustentar:

1. **El tema no está escrito como tal.** El proceso aparece solo como el paso 1 de Kimball. Hay que agregarlo al inicio de `03_modelo_estrella.md` (T2-01).
2. **El grano debe ser único, y en las anónimas no hay clave natural.** La regla `UNIQUE (producto_id, cliente_id, fecha)` de Plata no deduplica las reseñas anónimas, porque `cliente_id` es `NULL`. Para ellas solo aplica R10 (registros 100 % idénticos). Hay que documentarlo (T2-04).
3. **Los votos son acumulados.** El campo `helpfulness` no trae la fecha de cada voto: son los votos acumulados hasta la recolección. Las reseñas de 2013 tuvieron menos tiempo para recibir votos que las de 2012. Conviene comprobarlo en el recorte, comparando el % de reseñas con votos por mes, y advertirlo en los análisis de utilidad por mes (T2-06).
4. **El documento y el DDL no coinciden en algunos atributos.** El diagrama de `03_modelo_estrella.md` muestra menos atributos de `dim_fecha` que `ddl_gold.sql` (faltan `semestre`, `nombre_mes` y `dia`). Hay que alinearlos (T2-11).
5. **La volumetría de Oro está incompleta.** `01_exploracion_bd.md` estima "menos de 1,2 GB" contando un solo índice. Con los 5 índices de FK del DDL, el peor caso llega a ≈ 1,9 GB. Falta recalcularlo con las filas reales del recorte (T2-03, T2-10).
6. **El README nombra al compañero como "José".** Su nombre completo es José Julio Gómez Palmera (T2-11).

---

## 6. Lista de tareas

**Responsables por rol:** Arquitecto DW, José Julio (dueño del objetivo 2), y Data Engineer, Dario.
**Rama de trabajo:** `feature/modelo-dimensional`, con Pull Request hacia `dev`.

### Bloque A · Definir

**T2-01 · Declarar el tema y el proceso de negocio** · Arquitecto DW
- **Qué:** escribir el tema, el proceso y su justificación.
- **Cómo:**
  1. Copia la sección 1 de este plan al inicio de `03_modelo_estrella.md`.
  2. Explica en 3 o 4 líneas por qué no se modelan ventas: no hay campos de cantidad, pedido ni ingreso.
  3. Relaciona el tema con los 2 KGI.
- **Entregable:** sección "0. Tema y proceso de negocio" en `03_modelo_estrella.md`.

**T2-02 · Llenar la matriz de exploración de la guía (sección 23)** · Data Engineer
- **Qué:** una tabla con la fuente y las tablas de Plata: filas, columnas, clave, relaciones, calidad y observaciones.
- **Cómo:**
  1. Usa una fila para `all.txt.gz` y una por cada tabla de Plata (`producto`, `cliente`, `resena`).
  2. Saca las cifras de `01_exploracion_bd.md` y de tu bitácora de la exploración manual.
  3. Donde la guía dice ERP o CRM, escribe "Fuente única: SNAP".
- **Entregable:** matriz en `03_modelo_estrella.md`, sección "Datos de partida".

**T2-03 · Medir las filas reales del alcance** · Data Engineer
- **Qué:** contar los productos y clientes distintos, las reseñas anónimas y los días con reseñas, solo para 2012–2013.
- **Cómo:** ejecuta `python etl/02_conteo_recorte.py "<ruta>/all.txt.gz"`. El conteo de reseñas debe dar 5.627.079 como control.
- **Entregable:** las cifras anotadas en la bitácora y en la tabla de volumetría (T2-10).

**T2-04 · Declarar el grano y comprobar que es único** · Arquitecto DW
- **Qué:** la frase del grano, las alternativas descartadas y cómo se garantiza que una fila sea una reseña.
- **Cómo:**
  1. Escribe la frase del grano (sección 1.3).
  2. Explica por qué no se usa producto × día (sección 4).
  3. Documenta que R10 y R11 eliminan duplicados antes de Oro, y el caso de las anónimas (sección 5, punto 2).
- **Entregable:** sección "Grano" en `03_modelo_estrella.md`.

### Bloque B · Diseñar

**T2-05 · Justificar cada dimensión** · Arquitecto DW
- **Qué:** una ficha por dimensión.
- **Cómo:** para cada dimensión, llena una tabla con estas columnas:
  - Pregunta que responde (qué, quién, cuándo, qué tan satisfecho, qué tan útil).
  - Requerimientos que la usan, sacados de la matriz de bus.
  - Atributos y de dónde sale cada uno (campo de la fuente o derivado).
  - Jerarquías: `anio → semestre → trimestre → mes → dia` en Fecha, y `estrellas → sentimiento` en Calificación.
  - Filas especiales.
  
  Indica cuáles salen de una tabla de Plata y cuáles de un atributo (sección 2.1).
- **Entregable:** sección "Dimensiones" en `03_modelo_estrella.md`.

**T2-06 · Clasificar los hechos y escribir las fórmulas de los KPI** · Arquitecto DW
- **Qué:** cada medida con su tipo de aditividad y cada KPI con su fórmula.
- **Cómo:**
  1. Usa la tabla de la sección 3 de `03_modelo_estrella.md` y agrega estas fórmulas:
     - Calificación promedio = SUM(puntaje) / SUM(cantidad_resenas)
     - % útil = SUM(votos_utiles) / SUM(votos_totales)
     - Longitud promedio = SUM(longitud_texto) / SUM(cantidad_resenas)
  2. Agrega la nota de los votos acumulados (sección 5, punto 3).
- **Entregable:** sección "Hechos y KPI".

**T2-07 · Definir las claves y la tabla de linaje Plata → Oro** · Arquitecto DW + Data Engineer
- **Qué:** para cada columna de Oro, de qué columna de Plata sale y con qué regla.
- **Cómo:** usa una tabla con las columnas *columna de Oro · origen en Plata · regla*. Por ejemplo:
  - `cliente_sk`: de `silver.cliente.cliente_id`; si es `NULL`, va a -2.
  - `utilidad_sk`: de `votos_utiles / votos_totales`; si `votos_totales = 0`, va a 0.
- **Entregable:** sección "Claves y linaje". Será la especificación del ETL.

**T2-08 · Justificar el tratamiento histórico y las técnicas especiales** · Arquitecto DW
- **Qué:** SCD tipo 1, más la tabla de técnicas evaluadas.
- **Cómo:** copia y ajusta la sección 4 de este plan, citando las secciones 16 y 17 de la guía.
- **Entregable:** sección "Decisiones de diseño".

### Bloque C · Validar

**T2-09 · Validar con la matriz de bus y el checklist de la guía** · Arquitecto DW
- **Qué:** comprobar que cada requerimiento se responde y que cada dimensión se usa.
- **Cómo:**
  1. Revisa la matriz de bus requerimiento por requerimiento.
  2. Marca el checklist de la sección 8 de este plan.
  3. Si un requerimiento no se responde, ajusta el diseño; si una dimensión no se usa, elimínala.
- **Entregable:** checklist marcado en `03_modelo_estrella.md`.

**T2-10 · Volumetría de Oro y decisión de tablas o vistas** · Data Engineer
- **Qué:** filas × bytes por tabla de Oro, más los índices.
- **Cómo:**
  1. Para el hecho usa ≈ 72 bytes por fila: 48 de datos según los tipos de `ddl_gold.sql` más 24 de cabecera de PostgreSQL.
  2. Para las dimensiones usa las filas de T2-03.
  3. Con ese tamaño, justifica que Gold sean tablas físicas con índices y no vistas.
- **Entregable:** tabla "Volumetría de Oro" que reemplaza la estimación de `01_exploracion_bd.md`.

### Bloque D · Documentar y presentar

**T2-11 · Alinear la documentación** · Data Engineer
- **Qué:** que `03_modelo_estrella.md`, `ddl_gold.sql` y el README digan lo mismo.
- **Cómo:**
  1. Corrige los atributos de `dim_fecha` en el diagrama.
  2. Pon el nombre completo del compañero en el README.
  3. Enlaza este plan desde el README.
- **Entregable:** commit `docs: alinear modelo estrella con DDL`.

**T2-12 · Diagramar la estrella en draw.io** · Arquitecto DW
- **Qué:** dos diagramas.
  - **Conceptual:** la estrella con nombres de tablas, sin columnas.
  - **Lógico:** con columnas, PK, FK y tipos.
- **Cómo:**
  1. Sigue el estilo de `mer_drawio.xml`.
  2. Pon el hecho al centro y las 5 dimensiones alrededor, con relaciones N:1 en notación pata de gallo.
  3. Para el lógico también sirve importar `gold/drawsql_modelo_estrella.sql` en drawSQL.
- **Entregable:** `docs/modelado/diagramas/estrella_conceptual.drawio`, `estrella_logico.drawio` y sus PNG.

**T2-13 · Armar la presentación de la entrega** · Ambos
- **Qué:** diapositivas en el estilo del proyecto, **sin fechas del cronograma**.
- **Orden sugerido:**
  1. Tema y proceso.
  2. Del MER al modelo dimensional.
  3. Grano.
  4. Hechos y KPI.
  5. Dimensiones.
  6. Modelo estrella (diagrama).
  7. Matriz de bus.
  8. Decisiones y técnicas evaluadas.
  9. Volumetría de Oro.
- **Entregable:** archivo `.pptx` con el guion en las notas.

**T2-14 · Ensayar la sustentación** · Ambos
- **Qué:** responder sin leer las preguntas probables.
- **Cómo:** practica estas cinco:
  - ¿Por qué la reseña es el hecho y no una dimensión?
  - ¿Por qué no hay ventas?
  - ¿Por qué 5 dimensiones y no las 3 tablas?
  - ¿Qué pasa con las reseñas anónimas?
  - ¿Por qué el puntaje se promedia y no se suma?
- **Entregable:** respuestas en las notas de la presentación.

**T2-15 · Versionar** · Data Engineer
- **Qué:** subir todo a GitHub.
- **Cómo:**
  1. Trabaja en la rama `feature/modelo-dimensional`.
  2. Abre un Pull Request hacia `dev`.
  3. El otro integrante lo revisa antes de fusionar.
- **Entregable:** el Pull Request aprobado.

---

## 7. Orden de trabajo

```text
A · Definir       T2-01 ─┬─> T2-04
                  T2-02  │
                  T2-03 ─┼──────────────────────────> T2-10
B · Diseñar              └─> T2-05 ─> T2-06 ─> T2-07 ─> T2-08
C · Validar                                            T2-09 ─> T2-10
D · Presentar     T2-11 · T2-12 ─> T2-13 ─> T2-14 ─> T2-15
```

T2-03 puede correr mientras se escriben T2-01 y T2-04, porque tarda varios minutos sobre el archivo completo. La presentación (T2-13) va al final, cuando el diseño ya está validado.

---

## 8. Errores a evitar en este proyecto (guía, sección 22)

| Error de la guía | Cómo se vería aquí | Qué hacer |
|---|---|---|
| Comenzar por las tablas | Convertir `silver.resena` en `dim_resena` | La reseña es el **hecho** |
| Copiar el modelo operacional | Pasar las 3 tablas de Plata a Oro tal cual | 1 hecho + 5 dimensiones, 3 de ellas derivadas de atributos |
| Copiar el ejemplo de la guía | Crear `FactVentas`, `DimVendedor` o `DimUbicacion` | La fuente no tiene ventas, vendedores ni ubicación |
| Mezclar granularidades | Agregar totales mensuales al hecho de reseñas | Los agregados van en otra tabla o se calculan en Tableau |
| Crear dimensiones sin necesidad | Agregar `dim_categoria` | No hay categoría en `all.txt.gz`; queda como mejora futura |
| Historización sin necesidad | SCD tipo 2 en cliente o producto | El archivo está cerrado: basta con SCD tipo 1 |

---

## 9. Checklist de validación (guía, sección 25, adaptado)

**Requisitos**
- [ ] Responde a los objetivos del proyecto y a los 2 KGI.
- [ ] Permite los 20 requerimientos (matriz de bus).
- [ ] No agrega historización no requerida.

**Granularidad**
- [ ] La tabla de hechos tiene un grano escrito en una frase.
- [ ] Todas las dimensiones son compatibles con 1 fila = 1 reseña.
- [ ] Todas las medidas son de la reseña individual; no hay totales mezclados.

**Dimensiones**
- [ ] Cada dimensión tiene al menos un requerimiento que la usa.
- [ ] Hay claves subrogadas, la clave natural se conserva y existen las filas -1 y -2.
- [ ] Hay dimensión de fecha con calendario completo.

**Hechos**
- [ ] Se sabe cuáles son aditivos y cuáles se promedian.
- [ ] Los porcentajes se calculan al final, nunca se guardan sumados.

**Calidad**
- [ ] No hay claves duplicadas inesperadas (R10, R11).
- [ ] Los nulos se tratan con filas especiales, no con FK nulas.
- [ ] Cada transformación está documentada en la tabla de linaje (T2-07).
