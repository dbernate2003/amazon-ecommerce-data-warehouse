# Planteamiento del proyecto

Documento base de la primera entrega del segundo corte: introducción, objetivos, requerimientos y explicación de la base de datos.

---

## 1. Introducción

Las reseñas de Amazon influyen directamente en qué compran los clientes y qué productos tienen éxito. El dataset **Amazon Reviews** publicado por SNAP (Stanford) reúne 34,7 millones de reseñas entre 1995 y 2013, pero llega como un único archivo de texto plano de 11 GB comprimido, en formato `clave: valor`, sin tablas ni relaciones: así no puede responder preguntas de negocio.

Este proyecto construye una **bodega de datos con topología estrella** sobre los **últimos años del dataset (enero 2012 – marzo 2013, 5,6 millones de reseñas)**:

- **Motor de base de datos:** PostgreSQL, con un esquema por capa de la arquitectura Medallion (`bronze`, `silver`, `gold`).
- **Estructura de tablas:** el archivo plano se normaliza en un modelo relacional de tres tablas (`producto`, `cliente`, `resena`) en la capa Plata, y de ahí se construye el esquema estrella en la capa Oro. El paso a paso está en [`02_modelo_relacional.md`](../modelado/02_modelo_relacional.md).
- **Modelo entidad-relación:** un producto recibe muchas reseñas y un cliente escribe muchas reseñas; la reseña es la entidad central que relaciona a ambos.
- **Metodología:** Kimball para el diseño dimensional; Medallion para organizar el procesamiento; Tableau para el análisis.

---

## 2. Objetivo general

Implementar una bodega de datos analítica con topología estrella sobre 5,6 millones de reseñas de productos de Amazon (enero 2012 – marzo 2013), aplicando la metodología Kimball y la arquitectura Medallion en PostgreSQL, para analizar la calificación, la utilidad y el comportamiento de productos y clientes mediante KPI y KGI visualizados en Tableau.

---

## 3. Objetivos específicos

### 3.1 Comparación: objetivos de referencia vs. objetivos presentados

El profesor dio por buenos los cuatro objetivos de referencia. Los comparamos con los que presentamos el 29 de septiembre para unificarlos:

| # | Objetivo de referencia (aprobado) | Nuestro objetivo presentado | Qué se ajusta |
|---|---|---|---|
| 1 | Caracterizar la volumetría y estructura del origen para determinar las necesidades de almacenamiento e infraestructura | Caracterizar volumen, estructura y calidad de las 34,7 M reseñas para dimensionar el almacenamiento de cada capa | Se agrega la **exploración de la BD** y el **recorte a 5,6 M** (2012–2013) |
| 2 | Diseñar el modelo multidimensional en esquema estrella (capa Oro) que responda a los requerimientos analíticos | Diseñar el modelo estrella con Kimball: grano, hechos y 5 dimensiones | Ya estaba alineado; se precisa que responde los **20 requerimientos** |
| 3 | Implementar la arquitectura Medallion con pipelines ETL/ELT que aseguren limpieza, estandarización y calidad del dato | Extraer, transformar y cargar por capas con reglas de limpieza, claves subrogadas y fila -1 | Se unen **Medallion y ETL** en un solo objetivo, con **PostgreSQL** como motor |
| 4 | Desarrollar dashboards interactivos para el análisis visual y la toma de decisiones estratégicas | Construir dashboards en Power BI con KPI, KGI y storytelling | **Power BI → Tableau**, por pedido del profesor |

### 3.2 Objetivos específicos unificados

1. **Exploración y volumetría.** Explorar y caracterizar la base de datos fuente —estructura, calidad y volumen— y delimitar el alcance a 5,6 millones de reseñas (enero 2012 – marzo 2013) para dimensionar el almacenamiento de cada capa.
2. **Diseño multidimensional.** Diseñar el modelo en esquema estrella (capa Oro) con la metodología Kimball —grano, tabla de hechos y 5 dimensiones— que responda los 20 requerimientos analíticos.
3. **Arquitectura Medallion y ETL.** Implementar las capas Bronce, Plata y Oro en PostgreSQL mediante un proceso ETL con reglas de limpieza, estandarización y calidad del dato, claves subrogadas y filas especiales -1.
4. **Visualización en Tableau.** Desarrollar dashboards interactivos en Tableau, con KPI y KGI, filtros claros y storytelling, para apoyar la toma de decisiones.

| Objetivo | Entrega del cronograma | Rol responsable |
|---|---|---|
| 1. Exploración y volumetría | 29 sep (hecha) y 8 oct (reglas del EDA) | Data Engineer — Dario |
| 2. Diseño multidimensional | 30 sep | Arquitecto DW — José |
| 3. Medallion y ETL | 8 oct y 12 oct | Data Engineer / ETL Developer — Dario |
| 4. Visualización en Tableau | 15 oct | Analista BI — José |

---

## 4. Requerimientos

Preguntas de negocio que la bodega debe responder. Todas usan campos que existen en el dataset y alguna de las 5 dimensiones del modelo.

| ID | Pregunta de negocio | Métrica | Dimensiones |
|---|---|---|---|
| RQ-01 | ¿Cuál es la calificación promedio de cada producto? | Promedio de puntaje | Producto |
| RQ-02 | ¿Qué productos reciben más reseñas? | Cantidad de reseñas | Producto |
| RQ-03 | ¿Qué productos concentran más reseñas negativas (1-2 ★)? | Cantidad de reseñas | Producto, Calificación |
| RQ-04 | ¿Qué productos tienen la mejor calificación con al menos 100 reseñas? | Promedio y cantidad | Producto |
| RQ-05 | ¿Cómo se comparan los libros (ISBN) con los demás productos en volumen y calificación? | Cantidad y promedio | Producto (tipo) |
| RQ-06 | ¿Cómo se relaciona el rango de precio con la calificación (solo productos con precio)? | Promedio de puntaje | Producto (rango de precio) |
| RQ-07 | ¿Qué porcentaje de productos y de reseñas no tiene precio registrado? | % sin precio | Producto |
| RQ-08 | ¿Qué clientes escriben más reseñas? | Cantidad de reseñas | Cliente |
| RQ-09 | ¿Qué calificación promedio otorga cada cliente (exigentes vs. generosos)? | Promedio de puntaje | Cliente |
| RQ-10 | ¿Qué clientes escriben las reseñas más útiles para la comunidad? | Votos útiles | Cliente, Utilidad |
| RQ-11 | ¿Qué porcentaje de las reseñas es anónimo? | % de reseñas anónimas | Cliente |
| RQ-12 | ¿Cuántos clientes escriben una sola reseña frente a clientes recurrentes? | Cantidad de clientes | Cliente |
| RQ-13 | ¿Cómo evoluciona mes a mes la cantidad de reseñas (incluido el pico dic 2012 – feb 2013)? | Cantidad de reseñas | Fecha |
| RQ-14 | ¿Cómo evoluciona mes a mes la calificación promedio? | Promedio de puntaje | Fecha |
| RQ-15 | ¿Qué día de la semana se publican más reseñas? | Cantidad de reseñas | Fecha |
| RQ-16 | ¿Cambia la calificación entre fin de semana y días hábiles? | Promedio de puntaje | Fecha |
| RQ-17 | ¿Cómo se distribuyen las reseñas entre 1 y 5 estrellas? | Cantidad de reseñas | Calificación |
| RQ-18 | ¿Qué porcentaje de reseñas es positivo, neutral y negativo? | % de reseñas | Calificación (sentimiento) |
| RQ-19 | ¿Qué porcentaje de los votos recibidos marca las reseñas como útiles? | Votos útiles / votos totales | Utilidad |
| RQ-20 | ¿Las reseñas negativas se consideran más o menos útiles que las positivas? | % de utilidad | Calificación, Utilidad |

---

## 5. KPI y KGI (propuesta inicial — la valida el Analista BI)

**KGI (resultados de negocio):**

| KGI | Definición | Meta de referencia |
|---|---|---|
| Satisfacción del cliente | % de reseñas positivas (4-5 ★) | ≥ 80 % |
| Confianza de la comunidad | % de votos que marcan una reseña como útil | ≥ 70 % |

**KPI (indicadores que miden el avance hacia los KGI):**

| KPI | Fórmula | Aporta a |
|---|---|---|
| Calificación promedio | AVG(puntaje) | Satisfacción |
| % reseñas negativas | reseñas 1-2 ★ / total | Satisfacción |
| % de utilidad | SUM(votos_utiles) / SUM(votos_totales) | Confianza |
| % reseñas con votos | reseñas con votos_totales > 0 / total | Confianza |
| Reseñas por mes | COUNT(reseñas) por mes | Actividad |
| % reseñas anónimas | reseñas de cliente anónimo / total | Calidad del dato |

Las metas se ajustan cuando se perfile el recorte 2012–2013 (en todo el dataset, las positivas son 78,6 %).

---

## 6. La base de datos: qué datos maneja y qué objetivos tenemos con ella

**Qué datos maneja.** Cada registro es una reseña con 10 campos:

| Grupo | Campos | Destino en el modelo |
|---|---|---|
| Producto | `product/productId`, `product/title`, `product/price` | `silver.producto` → `gold.dim_producto` |
| Cliente | `review/userId`, `review/profileName` | `silver.cliente` → `gold.dim_cliente` |
| Reseña | `review/helpfulness`, `review/score`, `review/time`, `review/summary`, `review/text` | `silver.resena` → `gold.fact_resenas`, `dim_fecha`, `dim_calificacion`, `dim_utilidad` |

**Objetivos a futuro con la base de datos:**

1. Extender la carga del recorte 2012–2013 a los 34,7 M registros sin cambiar el diseño (solo cambia el filtro de fechas).
2. Incorporar las categorías de producto desde el archivo complementario `categories.txt.gz` de SNAP para crear una dimensión de categoría.
3. Analizar el texto de las reseñas (sentimiento, palabras frecuentes) en la capa Plata, donde se conserva el texto.
4. Automatizar cargas incrementales del ETL y conectar Tableau directamente a PostgreSQL.
