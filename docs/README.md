# Documentación del proyecto

La documentación está organizada **por área**. Cada área tiene un responsable, que mantiene sus documentos y revisa los Pull Requests que los tocan. La asignación automática de revisores está en [`.github/CODEOWNERS`](../.github/CODEOWNERS).

**Regla del equipo:** si necesitas un cambio en un documento de otra área, se lo pides a su responsable. No lo editas tú.

## Áreas

| Carpeta | Qué contiene | Responsable | Rol |
|---|---|---|---|
| [`negocio/`](negocio/) | Planteamiento, objetivos, requerimientos, KPI y KGI | Los dos | Equipo |
| [`datos/`](datos/) | Exploración de la fuente, perfil del dataset, volumetría y linaje | Dario Andrés Bernate Cañas | Data Engineer · ETL Developer |
| [`modelado/`](modelado/) | Modelo relacional (Plata), modelo estrella (Oro) y diagramas | José Julio Gómez Palmera | Arquitecto DW · Analista BI |
| [`gestion/`](gestion/) | Plan y tareas de cada entrega | Dario Andrés Bernate Cañas | PM |

## Documentos

| Documento | Contenido | Responsable |
|---|---|---|
| [`negocio/00_planteamiento.md`](negocio/00_planteamiento.md) | Introducción, objetivos, 20 requerimientos, KPI/KGI y objetivos a futuro | Los dos |
| [`datos/01_exploracion_bd.md`](datos/01_exploracion_bd.md) | Perfil de `all.txt.gz`, alcance 2012–2013, volumetría y reglas del EDA (R01–R13) | Dario |
| [`datos/perfil_dataset.json`](datos/perfil_dataset.json) | Salida completa de `etl/01_exploracion.py` sobre los 34,7 M registros | Dario |
| `datos/06_linaje_plata_oro.md` | Origen y regla de cada columna de Oro *(se crea en DB-04)* | Dario |
| [`modelado/02_modelo_relacional.md`](modelado/02_modelo_relacional.md) | Normalización del archivo plano a 3FN: `producto`, `cliente`, `resena` | José Julio |
| [`modelado/03_modelo_estrella.md`](modelado/03_modelo_estrella.md) | Diseño dimensional con Kimball: tema, grano, hechos y 5 dimensiones | José Julio |
| [`modelado/diagramas/mer_drawio.xml`](modelado/diagramas/mer_drawio.xml) | Modelo entidad-relación de la capa Plata (se abre en draw.io) | José Julio |
| `modelado/diagramas/estrella_conceptual.drawio` y `.png` | Estrella sin columnas *(se crea en JJ-07)* | José Julio |
| `modelado/diagramas/estrella_logico.png` | Estrella con columnas, PK y FK *(se crea en DB-06)* | Dario |
| [`gestion/04_plan_modelo_estrella.md`](gestion/04_plan_modelo_estrella.md) | Plan de la entrega del modelo estrella | Dario |
| [`gestion/05_tareas_modelo_estrella.md`](gestion/05_tareas_modelo_estrella.md) | Tareas JJ-, DB- y EQ- con dueño, pasos y criterio de terminado | Dario |

## Fuera de `docs/`

| Carpeta | Qué contiene | Responsable |
|---|---|---|
| `bronze/`, `silver/` | DDL de las capas Bronce y Plata | Dario |
| `gold/` | DDL del esquema estrella y versión para drawSQL | José Julio diseña · Dario implementa |
| `etl/`, `exploracion_manual/` | Scripts de exploración, conteos y pipeline ETL | Dario |
| `dashboard/` | Libros y capturas de Tableau | José Julio |

## Convenciones

- Los documentos se numeran en el orden en que se leen (`00_`, `01_`, …), aunque estén en carpetas distintas.
- Los diagramas van en `modelado/diagramas/`, con el archivo editable (`.drawio` o `.xml`) y su exportación en `.png`.
- Los archivos de datos (`*.gz`, muestras, `*.csv` fuera de `docs/`) no se versionan; ver `.gitignore`.
- Commits: `docs:` para documentos, `feat:` para scripts y DDL, `fix:` para correcciones.
