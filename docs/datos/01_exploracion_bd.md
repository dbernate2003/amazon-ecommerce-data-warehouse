# Exploración de la base de datos

Resultado del perfilamiento completo de `all.txt.gz`, ejecutado con `etl/01_exploracion.py` en streaming (sin descomprimir el archivo) sobre los 34.686.770 registros. Salida completa: [`perfil_dataset.json`](perfil_dataset.json). Tiempo de ejecución: 37 minutos.

> Los porcentajes de este documento se calcularon sobre **todo el dataset**. Una vez cargado el recorte 2012–2013 en Bronce, se vuelve a perfilar solo el recorte.

---

## 1. Estructura

| Verificación | Resultado |
|---|---|
| Registros | **34.686.770** (381.554.470 líneas) |
| Campos por registro | **10 en el 100 % de los registros**; ningún campo inesperado |
| Líneas con error de codificación (no UTF-8) | 0 |
| Registros sin línea en blanco separadora | 0 |
| Productos distintos (`product/productId`) | 2.441.053 |
| Usuarios distintos (`review/userId`) | 6.643.669 |

**Conclusión:** el archivo es estructuralmente limpio. Los problemas son de **calidad del dato**, no de formato.

---

## 2. Perfil por campo

| Campo | Tipo real | Nulos / "unknown" | Observación |
|---|---|---|---|
| `product/productId` | Texto de 10 caracteres | 0 % | 81,6 % ASIN (B + 9) y **18,4 % ISBN-10 (libros)**; 3 con formato no estándar |
| `product/title` | Texto (media 38 car.) | 0,03 % (11.203) | 722.394 títulos con entidades HTML (`&amp;`, `&quot;`) |
| `product/price` | Decimal 0 – 999,99 (media 25,64) | **62,1 % "unknown"** | Un solo precio por producto (dependencia funcional confirmada) |
| `review/userId` | Texto (A + alfanumérico) | **14,5 % "unknown"** | Reseñas anónimas; 3 valores con URL en lugar de ID |
| `review/profileName` | Texto (media 14 car.) | 14,5 % "unknown" | Coincide con los userId anónimos |
| `review/helpfulness` | Fracción `a/b` en el 100 % | 0 % | **32,2 % sin votos** (`x/0`); 86 casos con útiles > total |
| `review/score` | Decimal 1.0 – 5.0 | 0 % | 0 inválidos; siempre entero (`.0`) |
| `review/time` | Entero Unix (segundos, UTC) | 0 % | **150 con valor -1** (1969-12-31); el resto guarda solo el día, sin hora |
| `review/summary` | Texto (media 27 car.) | 0,002 % | 346.461 con entidades HTML |
| `review/text` | Texto (media 737 car., máx. 32.713) | 16 vacíos | 3.804.173 con entidades HTML |

### Calificaciones (todo el dataset)

| Estrellas | Reseñas | % |
|---|---|---|
| 5 ★ | 20.705.260 | 59,7 % |
| 4 ★ | 6.551.166 | 18,9 % |
| 3 ★ | 2.892.566 | 8,3 % |
| 2 ★ | 1.791.219 | 5,2 % |
| 1 ★ | 2.746.559 | 7,9 % |

Media **4,17**. Positivas (4-5 ★) 78,6 %, neutrales 8,3 %, negativas (1-2 ★) 13,1 %. La distribución tiene forma de "J": sesgo típico de las reseñas en línea.

### Duplicados

| Clave | Registros redundantes |
|---|---|
| Registro completo idéntico | **86.267** |
| Usuario + producto + fecha (sin anónimos) | **221.421** |
| Usuario + producto (sin anónimos) | 422.051 |

SNAP advierte que Amazon fusiona reseñas de productos equivalentes, lo que explica parte de los duplicados.

---

## 3. Distribución temporal y alcance

| Año | Reseñas | Año | Reseñas |
|---|---|---|---|
| 1995 | 1.214 | 2004 | 2.133.486 |
| 1996 | 27.895 | 2005 | 2.345.035 |
| 1997 | 181.040 | 2006 | 2.167.359 |
| 1998 | 787.929 | 2007 | 2.489.352 |
| 1999 | 2.137.727 | 2008 | 2.060.758 |
| 2000 | 2.140.371 | 2009 | 2.051.946 |
| 2001 | 1.930.312 | 2010 | 2.089.277 |
| 2002 | 2.011.901 | 2011 | 2.404.392 |
| 2003 | 2.099.547 | **2012** | **3.856.226** |
| (1969, inválidas) | 150 | **2013** | **1.770.853** |

### Decisión de alcance

El profesor aceptó trabajar con ~5 millones de registros tomando los últimos años. Se toma el período **1 de enero de 2012 – 4 de marzo de 2013** (última fecha real del archivo):

**5.627.079 reseñas** = 3.856.226 (2012) + 1.770.853 (2013).

Filtro técnico: `review/time >= 1325376000` (2012-01-01 00:00 UTC). Las 150 fechas inválidas (-1) quedan fuera del alcance automáticamente.

### Hallazgo clave: pico atípico dentro del alcance

| Mes | Reseñas | Mes | Reseñas |
|---|---|---|---|
| 2012-01 | 274.880 | 2012-09 | 323.663 |
| 2012-02 | 214.049 | 2012-10 | 337.045 |
| 2012-03 | 238.241 | 2012-11 | 459.391 |
| 2012-04 | 214.500 | **2012-12** | **894.674** |
| 2012-05 | 216.291 | **2013-01** | **1.037.101** |
| 2012-06 | 213.124 | **2013-02** | **708.975** |
| 2012-07 | 234.142 | 2013-03 (hasta el día 4) | 24.777 |
| 2012-08 | 236.226 | | |

Entre enero y octubre de 2012 el promedio es de ~250 mil reseñas al mes; de diciembre 2012 a febrero 2013 llega a ~880 mil. **Esos tres meses son el 47 % del alcance** (2.640.750 reseñas). Hay que investigarlo en el EDA del recorte (duplicados por fusión de productos, un tipo de producto dominante, etc.) y es material directo para el storytelling (RQ-13).

---

## 4. Volumetría del alcance (estimada)

Fórmula: **tamaño = registros × bytes por fila**. Bytes por registro crudo = 160 bytes de etiquetas + 861 de valores + 11 saltos de línea ≈ **1.032 bytes** (medias reales del perfil). Con eso, el archivo completo descomprimido ocupa ~35,8 GB (compresión gzip ≈ 3,1 : 1).

| Capa | Tabla | Filas | Bytes por fila | Tamaño estimado |
|---|---|---|---|---|
| Fuente | `all.txt.gz` completo | 34.686.770 | — | 11,7 GB (medido) |
| Bronce | `bronze.resenas_raw` | 5.627.079 | ~1.032 (texto crudo) | **~5,8 GB** |
| Plata | `silver.resena` | ≤ 5.627.079 | ~840 + índices | ~5,4 GB |
| Plata | `silver.producto` | ≤ 2.441.053 (cota superior) | ~90 | ≤ 0,22 GB |
| Plata | `silver.cliente` | ≤ 6.643.669 (cota superior) | ~55 | ≤ 0,37 GB |
| Oro | `gold.fact_resenas` | ≤ 5.627.079 | ~72 + índice | ~0,54 GB |
| Oro | 5 dimensiones | ≤ 9,1 M en total | 20 – 150 | < 0,6 GB |

**Lectura:** Oro ocupa menos de 1,2 GB frente a ~5,8 GB de Bronce, porque el texto de las reseñas se queda en Plata y el hecho solo guarda claves y métricas. Las filas de producto y cliente del recorte serán menos que las del dataset completo; se recalculan al perfilar el recorte.

---

## 5. Matriz de exploración

Resumen de cada fuente y tabla con la que se construye la bodega (guía de diseño, sección 23). Las filas de Plata son las reales del alcance 2012–2013, medidas en DB-01 (`exploracion_manual/bitacora.md`).

> **Fuente única.** La integración ERP + CRM de la guía no aplica: todo sale de `all.txt.gz` de SNAP.

| Fuente | Tabla / archivo | Filas | Columnas | Clave | Relaciones | Calidad | Observaciones |
|---|---|---|---|---|---|---|---|
| SNAP | `all.txt.gz` | 34.686.770 | 10 campos | Ninguna (no hay ID de reseña) | — (archivo plano) | Precio "unknown" 62,1 %; anónimas 14,5 %; HTML; 86.267 duplicados exactos; 150 fechas -1 | 11,7 GB comprimido |
| Bronce | `bronze.resenas_raw` | 5.627.079 | 13 (10 + `id_carga` + `archivo_origen` y `fecha_ingesta` de auditoría) | `id_carga` | — | Sin validar, por diseño | Todo como texto |
| Plata | `silver.producto` | 892.006 | 4 | `producto_id` | 1:N con reseña | Precio NULL | `tipo_producto` derivado |
| Plata | `silver.cliente` | 1.738.966 | 2 | `cliente_id` | 0..1:N con reseña | Las anónimas no crean fila | Nombre más reciente; anónimas del alcance: 5.382 (0,1 %) |
| Plata | `silver.resena` | ≤ 5.627.079 (después de R10 y R11) | 10 | `resena_id` | FK a producto y cliente | Restricciones R02, R07, R08 y R11 | Conserva el texto |

**De dónde sale cada cifra:** fuente → secciones 1 y 2 de este documento; Bronce → decisión de alcance (sección 3) y `bronze/ddl_bronze.sql`; Plata → `silver/ddl_silver.sql` y conteo DB-01.

**Lectura:** en el alcance, las reseñas anónimas bajan del 14,5 % del dataset completo al 0,1 %. Los porcentajes de la fila SNAP describen todo el archivo, no el recorte.

---

## 6. Reglas del EDA que pasan a la capa Plata

| ID | Regla | Origen del hallazgo |
|---|---|---|
| R01 | Leer el `.gz` en streaming por bloques; nunca descomprimir a disco | Tamaño (35,8 GB descomprimido) |
| R02 | Cargar solo reseñas con `review/time >= 1325376000` (desde 2012-01-01) | Decisión de alcance |
| R03 | Convertir `review/time` de Unix a `DATE` en UTC | Todas las fechas son de día exacto |
| R04 | `"unknown"` o vacío en `product/price` → `NULL` | 62,1 % sin precio |
| R05 | `review/userId = "unknown"` → cliente anónimo (`NULL` en Plata, SK -2 en Oro) | 14,5 % anónimas |
| R06 | Separar `review/helpfulness "a/b"` en `votos_utiles = a` y `votos_totales = b` | Formato fracción |
| R07 | Si `votos_utiles > votos_totales`, marcar como inconsistente y acotar `votos_utiles = votos_totales` | 86 casos |
| R08 | `review/score` a `SMALLINT` y validar dominio 1–5 | Siempre entero |
| R09 | Decodificar entidades HTML (`html.unescape`) en título, resumen y texto | 3,8 M textos afectados |
| R10 | Eliminar registros 100 % idénticos | 86.267 en todo el dataset |
| R11 | Deduplicar por usuario + producto + fecha, conservando la primera aparición | 221.421 en todo el dataset |
| R12 | Derivar `tipo_producto`: ISBN-10 (10 dígitos o 9 + X) → "Libro"; ASIN → "Otro" | 18,4 % libros |
| R13 | IDs con formato no estándar (URL en userId) → anónimo; registrar en bitácora | 3 casos |
