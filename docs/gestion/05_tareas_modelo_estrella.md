# Tareas de la entrega: tema y modelo estrella

Lista de tareas manuales para ejecutar el plan `04_plan_modelo_estrella.md` entre los dos integrantes **al mismo tiempo**. Cada tarea tiene un nombre, qué hacer, cómo hacerlo paso a paso, qué se entrega y cuándo se considera terminada.

| Integrante | Frente de trabajo | Prefijo |
|---|---|---|
| **José Julio Gómez Palmera** (Arquitecto DW · Analista BI) | **Diseño:** tema, grano, dimensiones, medidas, decisiones y validación | `JJ-` |
| **Dario Andrés Bernate Cañas** (Data Engineer · ETL Developer · PM) | **Datos y evidencia:** conteos, matriz, linaje, volumetría y documentación | `DB-` |
| Los dos | **Puntos de encuentro:** arranque, revisiones cruzadas y ensayo | `EQ-` |

---

## 1. Cómo trabajar a la par sin pisarse

### 1.1 Cada archivo tiene un solo dueño

Así nunca editan el mismo archivo al mismo tiempo y Git no genera conflictos.

| Archivo | Dueño | Rama |
|---|---|---|
| `docs/modelado/03_modelo_estrella.md` | José Julio | `feature/modelo-dimensional` |
| `docs/modelado/diagramas/estrella_conceptual.drawio` y `.png` | José Julio | `feature/modelo-dimensional` |
| Presentación de la entrega (`.pptx`) | José Julio la arma; Dario le pasa sus diapositivas | Fuera de Git, o en `docs/presentaciones/` |
| `docs/datos/01_exploracion_bd.md` (matriz y volumetría de Oro) | Dario | `docs/documentacion` |
| `docs/datos/06_linaje_plata_oro.md` (nuevo) | Dario | `docs/documentacion` |
| `docs/modelado/diagramas/estrella_logico.png` | Dario | `docs/documentacion` |
| `README.md` | Dario | `docs/documentacion` |
| `etl/02_conteo_recorte.py`, `exploracion_manual/*` | Dario | `feature/exploracion-bd` |

Si alguien necesita un cambio en un archivo que no es suyo, se lo pide al dueño. No lo edita.

Las carpetas de `docs/` siguen esta misma división por área: `negocio/`, `datos/`, `modelado/` y `gestion/`. El índice con el responsable de cada documento está en `docs/README.md`, y `.github/CODEOWNERS` hace que GitHub le pida la revisión al dueño de cada carpeta.

### 1.2 Cómo avanza cada frente

```text
             JOSÉ JULIO · diseño                       DARIO · datos y evidencia
             ─────────────────────────────────        ─────────────────────────────────
             EQ-01 Arranque y reparto (los dos)
Fase 1       JJ-01 Tema y proceso de negocio           DB-01 Conteo real del alcance  (corre solo)
             JJ-02 Grano de la tabla de hechos         DB-02 Matriz de exploración
                                                       DB-03 Prueba de votos acumulados
             ───────────── EQ-02 Revisión cruzada 1: tema, grano y cifras ─────────────
Fase 2       JJ-03 Fichas de las 5 dimensiones         DB-04 Linaje Plata → Oro
             JJ-04 Medidas y fórmulas de KPI           DB-05 Volumetría de la capa Oro
             JJ-05 Decisiones y técnicas evaluadas
             ───────────── EQ-03 Revisión cruzada 2: fichas, linaje y volumetría ─────────────
Fase 3       JJ-06 Validación con matriz de bus        DB-06 Diagrama lógico de la estrella
             JJ-07 Diagrama conceptual de la estrella  DB-07 Alinear README y documentación
             JJ-08 Presentación de la entrega          DB-08 Diapositivas de datos y volumetría
                                                       DB-09 Pull Requests y revisión
             ───────────── EQ-04 Ensayo de la sustentación ─────────────
```

**Carga estimada, contando los puntos de encuentro:**
- José Julio: unas 10 horas.
- Dario: unas 8 h 20 min, más el tiempo en que DB-01 corre solo sobre el archivo completo (mientras tanto avanza con DB-02).

Si José Julio se atrasa, Dario puede tomar JJ-07 (diagrama conceptual), porque para entonces ya tendrá hecho el lógico.

### 1.3 Cómo marcar el avance

Marquen la casilla `[x]` de cada tarea en este archivo, o importen `tareas_modelo_estrella_notion.csv` al tablero de Notion (sección 6).

---

## 2. Puntos de encuentro (los dos)

### EQ-01 · Arranque y reparto · 20 min

- [ ] **Qué:** que los dos empiecen con el mismo marco y sin conflictos en Git.
- **Cómo:**
  1. Lean juntos las secciones 1 a 4 de `04_plan_modelo_estrella.md`: tema, relacional frente a dimensional, los 17 pasos y las decisiones.
  2. Confirmen la tabla de dueños de la sección 1.1.
  3. Cada uno actualiza su rama desde `dev`:
     ```bash
     git checkout dev && git pull
     git checkout -b feature/modelo-dimensional    # José Julio
     git checkout -b docs/documentacion            # Dario (si ya existe: git checkout docs/documentacion && git merge dev)
     ```
  4. Dario arranca DB-01 en cuanto termina la reunión, porque tarda.
- **Entregable:** ramas listas y tareas asignadas.
- **Terminado cuando:** cada uno sabe qué archivo es suyo y qué entrega primero.

### EQ-02 · Revisión cruzada 1: tema, grano y cifras · 20 min

- [ ] **Qué:** cerrar las bases del diseño antes de las dimensiones.
- **Depende de:** JJ-01, JJ-02, DB-01, DB-02.
- **Cómo:**
  1. José Julio explica el tema y el grano en 1 minuto, sin leer.
  2. Dario muestra las cifras de DB-01 y la matriz de DB-02.
  3. Comprueben juntos:
     - ¿Las reglas R10 y R11 garantizan el grano "1 fila = 1 reseña"?
     - ¿Las filas reales de producto y cliente coinciden con lo que va a cada dimensión?
  4. Anoten cualquier cambio en una línea al final de este archivo ("Decisiones de la revisión 1").
- **Terminado cuando:** el tema y el grano quedan congelados; ya no se cambian sin hablarlo.

### EQ-03 · Revisión cruzada 2: fichas, linaje y volumetría · 30 min

- [ ] **Qué:** comprobar que diseño y datos dicen lo mismo.
- **Depende de:** JJ-03, JJ-04, DB-04, DB-05.
- **Cómo:**
  1. Recorran las fichas de dimensiones de José Julio atributo por atributo: cada atributo debe tener su fila en el linaje de Dario. Si falta alguno, se agrega al linaje o se quita de la ficha.
  2. Comprueben que la volumetría usa las filas reales de DB-01 y los tipos de `ddl_gold.sql`.
  3. José Julio revisa la nota de votos acumulados de DB-03 y la agrega a JJ-04 si aplica.
- **Terminado cuando:** no hay atributo sin origen ni tabla sin volumetría.

### EQ-04 · Ensayo de la sustentación · 40 min

- [ ] **Qué:** que cualquiera de los dos pueda sustentar todo el modelo.
- **Depende de:** JJ-08 y DB-08.
- **Cómo:**
  1. Presenten completo una vez, cronometrando.
  2. **Intercambien:** José Julio explica la volumetría y el linaje; Dario explica el grano y las dimensiones. Si el profesor pregunta a cualquiera, ambos deben responder.
  3. Respondan sin leer:
     - ¿Por qué la reseña es el hecho y no una dimensión?
     - ¿Por qué no hay ventas?
     - ¿Por qué 5 dimensiones si solo hay 3 tablas?
     - ¿Qué pasa con las reseñas anónimas?
     - ¿Por qué el puntaje se promedia y no se suma?
  4. Escriban las respuestas en las notas de la presentación.
- **Terminado cuando:** los dos responden las 5 preguntas sin apoyo.

---

## 3. Frente de José Julio · Diseño

### JJ-01 · Tema y proceso de negocio · 45 min

- [ ] **Qué:** declarar el tema del proyecto, que es el proceso de negocio y no una dimensión.
- **Cómo:**
  1. Abre `docs/modelado/03_modelo_estrella.md` y crea al inicio la sección **"0. Tema y proceso de negocio"**.
  2. Escribe tres líneas:
     - **Área:** experiencia del cliente y reputación de productos.
     - **Proceso:** publicación y valoración de reseñas de productos.
     - **Título:** *Análisis de la satisfacción del cliente y la reputación de productos de Amazon a partir de sus reseñas (enero 2012 – marzo 2013).*
  3. Copia la tabla de procesos candidatos (plan, sección 1.2) y explica **con tus palabras** por qué se descartan las ventas: la fuente no tiene cantidad, pedido ni ingreso.
  4. Cierra conectando el tema con los 2 KGI de `00_planteamiento.md`: Satisfacción (% de reseñas de 4-5 ★) y Confianza (% de votos útiles).
- **Entregable:** sección 0 de `03_modelo_estrella.md`.
- **Terminado cuando:** alguien que no conoce el proyecto entiende en 30 segundos qué se analiza y por qué no son ventas.

### JJ-02 · Grano de la tabla de hechos · 45 min

- [ ] **Qué:** declarar qué representa una fila de `fact_resenas` y cómo se garantiza.
- **Depende de:** JJ-01.
- **Cómo:**
  1. En `03_modelo_estrella.md`, sección "Grano", escribe la frase completa:
     > *Una fila de `fact_resenas` representa una reseña publicada por un cliente (o de forma anónima) sobre un producto en una fecha.*
  2. Agrega una tabla de **granos considerados**:

     | Grano | ¿Qué permite? | ¿Qué pierde? | Decisión |
     |---|---|---|---|
     | 1 reseña | Todos los requerimientos | — | **Elegido** |
     | Producto × día | Tendencias por producto | Cliente (RQ-08 a RQ-12) y utilidad por reseña (RQ-20) | Descartado |

  3. Explica **cómo se garantiza que una fila sea una reseña**:
     - R10 elimina los registros idénticos.
     - R11 elimina los repetidos por usuario + producto + fecha.
     - En las anónimas no hay usuario, así que solo aplica R10 (plan, sección 5, punto 2).
  4. Agrega la regla de la guía: **no se mezclan granos**. Los totales mensuales no van en este hecho.
- **Entregable:** sección "Grano" de `03_modelo_estrella.md`.
- **Terminado cuando:** la frase del grano cabe en una línea y responde quién, qué y cuándo.

### JJ-03 · Fichas de las 5 dimensiones · 1 h 30 min

- [ ] **Qué:** una ficha por dimensión que justifique por qué existe.
- **Depende de:** JJ-02.
- **Cómo:**
  1. Usa `gold/ddl_gold.sql` como **fuente de verdad de los atributos**. Si el diagrama de `03_modelo_estrella.md` no coincide con el DDL, corrige el diagrama; por ejemplo, a `dim_fecha` le faltan `semestre`, `nombre_mes` y `dia`.
  2. Llena esta ficha para cada dimensión. El ejemplo de Calificación ya está lleno:

     | Campo | dim_calificacion |
     |---|---|
     | Pregunta que responde | ¿Qué tan satisfecho quedó el cliente? |
     | Requerimientos (matriz de bus) | RQ-01 a RQ-04, RQ-17, RQ-18, RQ-20 |
     | Origen | Atributo `review/score` → `silver.resena.puntaje` (no es una tabla de Plata) |
     | Atributos | `calificacion_sk`, `estrellas`, `descripcion`, `sentimiento` |
     | Jerarquía | `estrellas` → `sentimiento` |
     | Filas | 5 + fila -1 "Desconocida" |
     | Tratamiento histórico | Estática: no cambia |

  3. Haz las otras 4 fichas: Producto, Cliente, Fecha y Utilidad.
     - Producto y Cliente vienen de una tabla de Plata.
     - Fecha, Calificación y Utilidad nacen de un **atributo de la reseña** (plan, sección 2.1).
  4. Para el número de filas de Producto y Cliente usa las cifras de DB-01. Mientras llegan, escribe "pendiente DB-01".
- **Entregable:** sección "Dimensiones" de `03_modelo_estrella.md`, con 5 fichas.
- **Terminado cuando:** cada dimensión tiene al menos un requerimiento y cada atributo tiene origen.

### JJ-04 · Medidas y fórmulas de KPI · 1 h

- [ ] **Qué:** definir cada medida del hecho y cómo se calculan los KPI y KGI.
- **Depende de:** JJ-02. La nota final depende de DB-03.
- **Cómo:**
  1. Llena la tabla de medidas:

     | Medida | Tipo | Cómo se agrega | Origen |
     |---|---|---|---|
     | `cantidad_resenas` | Aditiva | SUM | Constante 1 por fila |
     | `puntaje` | Se promedia | SUM(puntaje) / SUM(cantidad_resenas) | `review/score` |
     | `votos_utiles` | Aditiva | SUM | `review/helpfulness`, la *a* de *a/b* |
     | `votos_totales` | Aditiva | SUM | `review/helpfulness`, la *b* de *a/b* |
     | `longitud_texto` | Aditiva | SUM, o promedio con `cantidad_resenas` | Largo de `review/text` |

  2. Escribe las fórmulas de los KPI de `00_planteamiento.md`, sección 5, usando las columnas del hecho. Ejemplos:
     - % de utilidad = SUM(`votos_utiles`) / SUM(`votos_totales`)
     - % de reseñas negativas = reseñas con `sentimiento` = 'Negativa' / SUM(`cantidad_resenas`)
  3. Agrega la regla de oro: **los porcentajes se calculan al final y nunca se suman**.
  4. Cuando Dario termine DB-03, agrega una nota sobre si los votos son acumulados y qué cuidado exige al analizar la utilidad por mes.
- **Entregable:** sección "Hechos y KPI" de `03_modelo_estrella.md`.
- **Terminado cuando:** cada KPI se puede calcular solo con columnas del modelo.

### JJ-05 · Decisiones de diseño y técnicas evaluadas · 45 min

- [ ] **Qué:** dejar escrito por qué el modelo es así y qué técnicas se evaluaron.
- **Depende de:** JJ-03 y JJ-04.
- **Cómo:**
  1. Copia las dos tablas de la sección 4 del plan: decisiones y técnicas especiales.
  2. Reescribe cada "por qué" **con tus palabras**. Si no puedes explicar una fila, pregúntale a Dario o revisa la guía (secciones 16, 17 y 20).
  3. Decide y justifica en 2 líneas si mantienes Calificación y Utilidad separadas o las unes en una *junk dimension*.
- **Entregable:** sección "Decisiones de diseño" de `03_modelo_estrella.md`.
- **Terminado cuando:** cada decisión tiene la alternativa descartada y su motivo.

### JJ-06 · Validación con matriz de bus y checklist · 45 min

- [ ] **Qué:** probar que el diseño responde los 20 requerimientos y cumple la guía.
- **Depende de:** EQ-03.
- **Cómo:**
  1. Revisa la matriz de bus de `03_modelo_estrella.md` requerimiento por requerimiento. Para cada uno, escribe qué medida y qué atributo de dimensión lo responden. Por ejemplo: RQ-15 → `cantidad_resenas` por `dim_fecha.nombre_dia`.
  2. Marca el checklist de la sección 9 del plan.
  3. Si un requerimiento no se puede responder, ajusta el diseño (o el requerimiento) y avísale a Dario para el linaje.
- **Entregable:** matriz de bus con columna "se responde con" y checklist marcado.
- **Terminado cuando:** los 20 requerimientos tienen su "se responde con" y el checklist está completo.

### JJ-07 · Diagrama conceptual de la estrella · 45 min

- [ ] **Qué:** el dibujo de la estrella **sin columnas**: solo tablas, relaciones y el grano.
- **Depende de:** JJ-03.
- **Cómo:**
  1. Abre draw.io (app.diagrams.net) y usa los mismos colores de `mer_drawio.xml`.
  2. Pon `fact_resenas` al centro con la etiqueta del grano y las 5 dimensiones alrededor.
  3. Une cada dimensión con el hecho con una relación N:1 en notación pata de gallo: el "muchos" va del lado del hecho.
  4. Debajo de cada dimensión escribe la pregunta que responde: qué, quién, cuándo, qué tan satisfecho, qué tan útil.
  5. Guárdalo como `docs/modelado/diagramas/estrella_conceptual.drawio` y expórtalo en PNG (Archivo → Exportar como → PNG).
- **Entregable:** `.drawio` y `.png` del modelo conceptual.
- **Terminado cuando:** se entiende el modelo sin leer ningún documento.

### JJ-08 · Presentación de la entrega · 2 h

- [ ] **Qué:** las diapositivas del modelo estrella para el profesor.
- **Depende de:** JJ-06, JJ-07 y DB-08.
- **Cómo:**
  1. Usa el estilo de la presentación de la primera entrega: colores, tipografía y etiquetas de objetivo. **Sin fechas del cronograma.**
  2. Orden sugerido:
     1. Tema y proceso de negocio (JJ-01).
     2. Del MER al modelo dimensional (diapositiva 6 de la primera entrega).
     3. Grano (JJ-02).
     4. Medidas y KPI (JJ-04).
     5. Dimensiones (JJ-03).
     6. Modelo estrella, con los diagramas de JJ-07 y DB-06.
     7. Matriz de bus (JJ-06).
     8. Decisiones (JJ-05).
     9. Diapositivas de Dario (DB-08).
  3. Escribe el guion de cada diapositiva en las notas del orador.
- **Entregable:** archivo `.pptx` de la entrega.
- **Terminado cuando:** se presenta completa sin pasarse del tiempo que pida el profesor.

---

## 4. Frente de Dario · Datos y evidencia

### DB-01 · Conteo real del alcance · 15 min de trabajo + ejecución

- [ ] **Qué:** medir las filas reales de 2012–2013 que necesitan las dimensiones y la volumetría.
- **Cómo:**
  1. Copia `02_conteo_recorte.py` en `etl/`.
  2. En Git Bash:
     ```bash
     F=~/Downloads/all.txt.gz
     time python etl/02_conteo_recorte.py "$F"
     ```
  3. Mientras corre, avanza con DB-02.
  4. Anota en `exploracion_manual/bitacora.md` las 6 cifras y el tiempo de ejecución.
  5. Pásale a José Julio las filas de producto y cliente.
- **Entregable:** reseñas del alcance, productos distintos, clientes distintos, anónimas, % de anónimas y días con reseñas.
- **Terminado cuando:** "Reseñas del alcance" da **5.627.079**. Ese es el control: si da otra cifra, revisa el filtro antes de seguir.

### DB-02 · Matriz de exploración · 45 min

- [ ] **Qué:** la matriz de la guía (sección 23), adaptada a una fuente única.
- **Cómo:**
  1. En `docs/datos/01_exploracion_bd.md`, agrega la sección **"Matriz de exploración"** con esta tabla. Ya trae los datos documentados; completa lo marcado como *DB-01*:

     | Fuente | Tabla / archivo | Filas | Columnas | Clave | Relaciones | Calidad | Observaciones |
     |---|---|---|---|---|---|---|---|
     | SNAP | `all.txt.gz` | 34.686.770 | 10 campos | Ninguna (no hay ID de reseña) | — (archivo plano) | Precio "unknown" 62,1 %; anónimas 14,5 %; HTML; 86.267 duplicados exactos; 150 fechas -1 | 11,7 GB comprimido |
     | Bronce | `bronze.resenas_raw` | 5.627.079 | 13 (10 + `id_carga` + 2 de auditoría) | `id_carga` | — | Sin validar, por diseño | Todo como texto |
     | Plata | `silver.producto` | *DB-01* | 4 | `producto_id` | 1:N con reseña | Precio NULL | `tipo_producto` derivado |
     | Plata | `silver.cliente` | *DB-01* | 2 | `cliente_id` | 0..1:N con reseña | Las anónimas no crean fila | Nombre más reciente |
     | Plata | `silver.resena` | ≤ 5.627.079 (después de R10 y R11) | 10 | `resena_id` | FK a producto y cliente | Restricciones R02, R07, R08 y R11 | Conserva el texto |

  2. Revisa cada cifra contra `01_exploracion_bd.md`, `ddl_silver.sql` y tu bitácora.
  3. Agrega una nota: *"Fuente única. La integración ERP + CRM de la guía no aplica."*
- **Entregable:** sección "Matriz de exploración" en `01_exploracion_bd.md`.
- **Terminado cuando:** no queda ninguna celda vacía ni con *DB-01*.

### DB-03 · Prueba de votos acumulados · 30 min

- [ ] **Qué:** comprobar si las reseñas más recientes tienen menos votos porque tuvieron menos tiempo para recibirlos (plan, sección 5, punto 3).
- **Cómo:**
  1. Si todavía no tienes la muestra del 1 %, créala con la sección 0.3 de `guia_exploracion_manual.md`.
  2. Copia `votos_por_mes.py` en `exploracion_manual/` y ejecútalo:
     ```bash
     M=~/Downloads/muestra_1pct.txt
     python exploracion_manual/votos_por_mes.py "$M"
     # Para las cifras finales (tarda más):
     # gzip -dc "$F" | python exploracion_manual/votos_por_mes.py -
     ```
  3. Lee la tabla: mes, reseñas, % con votos, votos por reseña y % útiles.
  4. Interpreta:
     - Si el **% con votos baja** de 2012 a 2013, los votos son acumulados. Comparar la utilidad entre meses no es justo.
     - Si el **% útiles** se mantiene estable, la proporción sí se puede comparar.
  5. Escribe la conclusión en 3 líneas en la bitácora y pásasela a José Julio para JJ-04.
- **Entregable:** tabla por mes y conclusión en la bitácora.
- **Terminado cuando:** hay una conclusión clara: "los votos son o no son acumulados", con las cifras que lo muestran.

### DB-04 · Linaje Plata → Oro · 1 h 30 min

- [ ] **Qué:** para **cada columna** de la capa Oro, de dónde sale y con qué regla. Este documento será la especificación del ETL.
- **Cómo:**
  1. Abre `gold/ddl_gold.sql` y `silver/ddl_silver.sql` lado a lado.
  2. Crea `docs/datos/06_linaje_plata_oro.md` con una tabla por tabla de Oro, con estas columnas:

     | Columna de Oro | Origen en Plata | Regla de transformación | Si falta el dato |
     |---|---|---|---|

  3. Cubre todas las columnas del DDL:
     - **fact_resenas:** `resena_id`, `producto_sk`, `cliente_sk`, `fecha_sk`, `calificacion_sk`, `utilidad_sk`, `cantidad_resenas`, `puntaje`, `votos_utiles`, `votos_totales`, `longitud_texto`, `fecha_carga`.
     - **dim_producto**, **dim_cliente** y **dim_fecha**: todas sus columnas.
     - **dim_calificacion** y **dim_utilidad**: son filas fijas; documenta que se cargan con `INSERT` y no desde Plata.
  4. Filas de ejemplo para guiarte:

     | Columna de Oro | Origen en Plata | Regla | Si falta |
     |---|---|---|---|
     | `fact_resenas.cliente_sk` | `silver.resena.cliente_id` | Buscar `cliente_sk` en `dim_cliente` por `cliente_id` | NULL → **-2** Anónimo; sin coincidencia → **-1** |
     | `fact_resenas.fecha_sk` | `silver.resena.fecha` | `TO_CHAR(fecha, 'YYYYMMDD')` como entero | Sin coincidencia → **-1** |
     | `fact_resenas.utilidad_sk` | `votos_utiles`, `votos_totales` | totales = 0 → 0; % útil < 40 → 1; de 40 a menos de 70 → 2; ≥ 70 → 3 | — |
     | `fact_resenas.longitud_texto` | `silver.resena.texto` | `LENGTH(texto)` | Texto NULL → 0 (la columna de Oro es NOT NULL) |

  5. **Decide y documenta tres casos que el DDL todavía no resuelve:**
     - `dim_producto.titulo` es `VARCHAR(500)` y en Plata es `TEXT`. ¿Se recorta a 500 caracteres?
     - `dim_cliente.nombre_perfil` es `NOT NULL` en Oro, pero en Plata puede ser NULL. ¿Qué valor se pone?
     - Los límites de `rango_precio`: ¿un precio de exactamente 10 va en "< $10" o en "$10-$25"?
- **Entregable:** `docs/datos/06_linaje_plata_oro.md`.
- **Terminado cuando:** todas las columnas del DDL de Oro tienen origen, regla y caso de dato faltante.

### DB-05 · Volumetría de la capa Oro · 1 h

- [ ] **Qué:** el tamaño de cada tabla de Oro con las filas reales, y la decisión de usar tablas o vistas.
- **Depende de:** DB-01.
- **Cómo:**
  1. Calcula los bytes por fila sumando los tipos de `ddl_gold.sql` más 24 bytes de cabecera de PostgreSQL:
     - INTEGER = 4
     - SMALLINT = 2
     - BIGINT = 8
     - TIMESTAMP = 8
     - BOOLEAN = 1
     - Textos: su largo medio + 1
  2. Comprueba el del hecho: 8 + 12 + 4 + 4 + 12 + 8 = 48 de datos + 24 de cabecera ≈ **72 bytes por fila**.
  3. Llena esta tabla con las filas de DB-01:

     | Tabla | Filas | Bytes por fila | Datos | Índices (≈ 22 B por fila y por índice) | Total |
     |---|---|---|---|---|---|
     | `fact_resenas` | ≤ 5.627.079 | ≈ 72 | | PK + 5 FK | |
     | `dim_producto` | *DB-01* | ≈ 110 | | PK + UNIQUE | |
     | `dim_cliente` | *DB-01* + 2 | ≈ 72 | | PK + UNIQUE | |
     | `dim_fecha` | 732 | ≈ 72 | | PK + UNIQUE | |
     | `dim_calificacion` | 6 | — | Despreciable | | |
     | `dim_utilidad` | 5 | — | Despreciable | | |

  4. Reemplaza en `01_exploracion_bd.md` la frase "Oro menor a 1,2 GB" por tu resultado.
  5. Escribe 3 líneas justificando que Gold sean **tablas físicas con índices**, no vistas: son unos 5,6 M de filas, Tableau consulta mucho y las vistas recalcularían las uniones en cada consulta (guía, sección 20).
  6. Anota cómo se medirá el tamaño real cuando la capa exista:
     ```sql
     SELECT pg_size_pretty(pg_total_relation_size('gold.fact_resenas'));
     ```
- **Entregable:** sección "Volumetría de Oro" en `01_exploracion_bd.md`.
- **Terminado cuando:** cada tabla de Oro tiene filas, bytes y total, y la decisión de tablas o vistas está escrita.

### DB-06 · Diagrama lógico de la estrella · 30 min

- [ ] **Qué:** la estrella **con columnas**, PK, FK y tipos.
- **Depende de:** EQ-03, porque el linaje puede cambiar algún tipo.
- **Cómo:**
  1. Entra a drawsql.app y crea un diagrama nuevo con PostgreSQL.
  2. Usa *Import → SQL* y pega `gold/drawsql_modelo_estrella.sql`.
  3. Acomoda `fact_resenas` al centro y las 5 dimensiones alrededor.
  4. Exporta en PNG y guárdalo como `docs/modelado/diagramas/estrella_logico.png`.
  5. Revisa que coincida con el diagrama conceptual de José Julio (JJ-07): mismas tablas, mismas relaciones.
- **Entregable:** `estrella_logico.png`.
- **Terminado cuando:** el diagrama coincide con `ddl_gold.sql` columna por columna.

### DB-07 · Alinear README y documentación · 30 min

- [ ] **Qué:** que el README describa el proyecto actual.
- **Cómo:**
  1. En la tabla de equipo, cambia "José" por **José Julio Gómez Palmera**.
  2. En la tabla de documentación, agrega `04_plan_modelo_estrella.md`, `05_tareas_modelo_estrella.md` y `06_linaje_plata_oro.md`.
  3. Agrega debajo del título una línea con el tema del proyecto (JJ-01).
  4. Revisa que los enlaces apunten a `docs/` y funcionen en GitHub.
- **Entregable:** commit `docs: actualizar README con tema y nuevos documentos`.
- **Terminado cuando:** todos los enlaces del README abren el archivo correcto en GitHub.

### DB-08 · Diapositivas de datos y volumetría · 1 h

- [ ] **Qué:** 3 diapositivas para la presentación que arma José Julio.
- **Depende de:** DB-02, DB-04 y DB-05.
- **Cómo:**
  1. Haz las diapositivas en el mismo estilo de la primera entrega y **sin fechas del cronograma**:
     - **Datos de partida:** la matriz de exploración resumida (DB-02).
     - **Del dato a la estrella:** 4 filas de ejemplo del linaje, por ejemplo anónimo → -2 y votos → rango de utilidad (DB-04).
     - **Volumetría de Oro:** la tabla de DB-05 y la decisión de tablas o vistas.
  2. Escribe el guion en las notas del orador.
  3. Envíaselas a José Julio para JJ-08.
- **Entregable:** 3 diapositivas con notas.
- **Terminado cuando:** José Julio las integra a la presentación.

### DB-09 · Pull Requests y revisión · 30 min

- [ ] **Qué:** subir el trabajo de los dos a `dev` con revisión cruzada.
- **Cómo:**
  1. Cada uno abre su Pull Request hacia `dev`:
     - `feature/modelo-dimensional` (José Julio).
     - `docs/documentacion` y `feature/exploracion-bd` (Dario).
  2. **Revisión cruzada:** Dario revisa el PR de José Julio y José Julio revisa los de Dario, usando el checklist del plan (sección 9).
  3. Fusionen en `dev` y, antes de sustentar, `dev` en `main`.
  4. Mensajes de commit: `docs:` para documentos, `feat:` para scripts.
- **Entregable:** Pull Requests aprobados y fusionados.
- **Terminado cuando:** `main` tiene la versión que se va a sustentar.

---

## 5. Resumen de tareas

| ID | Nombre | Responsable | Fase | Depende de | Tiempo |
|---|---|---|---|---|---|
| EQ-01 | Arranque y reparto | Los dos | 1 | — | 20 min |
| JJ-01 | Tema y proceso de negocio | José Julio | 1 | EQ-01 | 45 min |
| JJ-02 | Grano de la tabla de hechos | José Julio | 1 | JJ-01 | 45 min |
| DB-01 | Conteo real del alcance | Dario | 1 | EQ-01 | 15 min + ejecución |
| DB-02 | Matriz de exploración | Dario | 1 | EQ-01 | 45 min |
| DB-03 | Prueba de votos acumulados | Dario | 1 | EQ-01 | 30 min |
| EQ-02 | Revisión cruzada 1: tema, grano y cifras | Los dos | 1 | JJ-02, DB-01, DB-02 | 20 min |
| JJ-03 | Fichas de las 5 dimensiones | José Julio | 2 | EQ-02 | 1 h 30 min |
| JJ-04 | Medidas y fórmulas de KPI | José Julio | 2 | EQ-02, DB-03 | 1 h |
| JJ-05 | Decisiones y técnicas evaluadas | José Julio | 2 | JJ-03, JJ-04 | 45 min |
| DB-04 | Linaje Plata → Oro | Dario | 2 | EQ-02 | 1 h 30 min |
| DB-05 | Volumetría de la capa Oro | Dario | 2 | DB-01 | 1 h |
| EQ-03 | Revisión cruzada 2: fichas, linaje y volumetría | Los dos | 2 | JJ-03, JJ-04, DB-04, DB-05 | 30 min |
| JJ-06 | Validación con matriz de bus y checklist | José Julio | 3 | EQ-03 | 45 min |
| JJ-07 | Diagrama conceptual de la estrella | José Julio | 3 | JJ-03 | 45 min |
| DB-06 | Diagrama lógico de la estrella | Dario | 3 | EQ-03 | 30 min |
| DB-07 | Alinear README y documentación | Dario | 3 | JJ-01 | 30 min |
| DB-08 | Diapositivas de datos y volumetría | Dario | 3 | DB-02, DB-04, DB-05 | 1 h |
| JJ-08 | Presentación de la entrega | José Julio | 3 | JJ-06, JJ-07, DB-08 | 2 h |
| DB-09 | Pull Requests y revisión | Dario (los dos revisan) | 3 | JJ-08 | 30 min |
| EQ-04 | Ensayo de la sustentación | Los dos | 3 | JJ-08, DB-08 | 40 min |

---

## 6. Cargar las tareas en Notion

`tareas_modelo_estrella_notion.csv` trae las 21 tareas con nombre, responsable, rol, fase, dependencias, descripción corta y estado "⏳ Pendiente". Para cargarlo:
1. Abre la base de datos **Tareas — 2do corte** en Notion.
2. Menú `•••` de la base → **Merge with CSV** y elige el archivo.
3. Revisa que las columnas coincidan; las que no existan en la base se crean nuevas.

La descripción completa de cada tarea (qué y cómo) está en este documento. En Notion basta con el resumen y el enlace a esta sección del repositorio.

---

## Decisiones de la revisión 1

*(Se llena en EQ-02.)*

## Decisiones de la revisión 2

*(Se llena en EQ-03.)*
