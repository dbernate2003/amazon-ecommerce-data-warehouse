# Guía del repositorio: roles, ramas y commits por fase

Reglas que usan los dos integrantes para trabajar en el repositorio [`amazon-ecommerce-data-warehouse`](https://github.com/dbernate2003/amazon-ecommerce-data-warehouse) sin pisarse. Para la entrega del modelo estrella, esta guía manda sobre lo que dicen de commits e integración la sección 1 y la tarea DB-09 de `05_tareas_modelo_estrella.md`.

**Las tres reglas de oro:**
1. **Cada carpeta tiene un dueño.** Solo el dueño la edita. Si necesitas un cambio en algo que no es tuyo, se lo pides.
2. **Una fase = un commit por rama.** No se hace un commit por tarea. Al cerrar la fase haces un solo commit con todo lo de esa fase en esa rama.
3. **Se integra al final de cada fase.** Haces push, abres un Pull Request hacia `dev`, el otro lo revisa en el punto de encuentro y se fusiona.

---

## 1. Equipo y roles

| Integrante | Roles | En GitHub (CODEOWNERS) |
|---|---|---|
| **Dario Andrés Bernate Cañas** | Data Engineer · ETL Developer · PM | `@dbernate2003` |
| **José Julio Gómez Palmera** | Arquitecto DW · Analista BI | `jjuliogomez@unicesar.edu.co` |

---

## 2. Estructura del repositorio y dueños

```text
amazon-ecommerce-data-warehouse/
├── .github/CODEOWNERS        Dueño de cada carpeta (GitHub asigna el revisor)   Dario
├── README.md                 Portada del proyecto                               Dario
├── bronze/                   DDL de la capa Bronce                              Dario
├── silver/                   DDL de la capa Plata                               Dario
├── gold/                     DDL del esquema estrella y versión drawSQL         José Julio diseña · Dario implementa
├── etl/                      Scripts de exploración, conteo y ETL               Dario
├── exploracion_manual/       Bitácora y scripts de pruebas sobre los datos      Dario
├── dashboard/                Libros y capturas de Tableau                       José Julio
└── docs/
    ├── README.md             Índice de documentos con su responsable            Dario
    ├── negocio/              00_planteamiento                                   Los dos
    ├── datos/                01_exploracion_bd, perfil_dataset.json, 06_linaje  Dario
    ├── modelado/             02_modelo_relacional, 03_modelo_estrella           José Julio
    │   └── diagramas/        mer_drawio.xml, estrella_conceptual, estrella_logico.png (este último, Dario)
    ├── gestion/              04_plan, 05_tareas, esta guía                      Dario
    └── presentaciones/       .pptx de cada entrega                              José Julio
```

**Reglas de la estructura:**
- Un documento nuevo va en la carpeta de su área, numerado en orden de lectura (`06_`, `07_`, …).
- Los diagramas van en `docs/modelado/diagramas/`, con el editable (`.drawio` o `.xml`) y su `.png`.
- Los datos no se versionan: `all.txt.gz`, las muestras (`muestra_*.txt`) y los `.csv` fuera de `docs/` están en `.gitignore`. Se quedan en `~/Downloads`.
- **Solo Dario marca las casillas `[x]` de `05_tareas_modelo_estrella.md`** y escribe las "Decisiones de la revisión". José Julio le avisa cuando termina una tarea.
- **`gold/ddl_gold.sql` no se edita durante la entrega del modelo estrella**, salvo que lo acuerden en EQ-03. En ese caso lo cambia José Julio en su commit de la fase 3.

---

## 3. Ramas

| Rama | Para qué | Quién escribe en ella |
|---|---|---|
| `main` | Versión que se sustenta ante el profesor | Nadie directo: solo recibe `dev` al final de cada entrega |
| `dev` | Integración de los dos | Nadie directo: solo recibe Pull Requests |
| `feature/exploracion-bd` | Scripts y bitácora de pruebas sobre los datos (`etl/`, `exploracion_manual/`) | Dario |
| `docs/documentacion` | Documentos de datos y gestión, README, diagrama lógico | Dario |
| `feature/modelo-dimensional` | Modelo estrella, diagramas conceptuales y presentación | José Julio |
| `feature/etl-medallion` | Carga de Bronce, Plata y Oro (próxima entrega) | Dario |
| `feature/dashboard` | Tableau (entrega de visualización) | José Julio |

Las ramas **no se borran** al fusionar el Pull Request: se reutilizan en la fase siguiente.

---

## 4. Ciclo de una fase

### 4.1 Al empezar la fase: traer lo último de `dev`

```bash
git checkout <tu-rama>
git fetch origin
git merge --ff-only origin/dev
```

Si `--ff-only` falla, es porque tu Pull Request anterior todavía no se fusionó. Fusiónalo primero, o usa `git merge origin/dev`.

### 4.2 Durante la fase: trabajar sin commits

Haz las tareas de la fase. No hagas commit por tarea. Si necesitas cambiar de rama a mitad de camino, guarda el trabajo con `git stash` y recupéralo con `git stash pop`.

### 4.3 Al cerrar la fase: un commit y push

```bash
git status                               # solo deben aparecer archivos de tu área
git add <archivos de la fase>            # nunca "git add ." a ciegas
git diff --cached --stat                 # revisa qué va en el commit
git commit -m "<título>" -m "<cuerpo>"   # los mensajes están en la sección 5
git push -u origin <tu-rama>
```

### 4.4 Integrar: Pull Request hacia `dev`

1. En GitHub: **Pull requests → New** · base: `dev` ← compare: `<tu-rama>`.
2. Título del PR = título del commit. GitHub asigna al revisor por CODEOWNERS.
3. El otro lo revisa en el punto de encuentro (EQ-02, EQ-03 o EQ-04).
4. Se fusiona con **"Create a merge commit"**. No se usa *squash* ni *rebase*, para que la rama siga alineada con `dev`.
5. No borres la rama.

### 4.5 Formato de los mensajes

```text
<tipo>(fase-<N>): <qué se logró, en minúsculas y sin punto final>

- <ID de tarea>: <qué archivo cambió y qué contiene>
```

| Tipo | Cuándo |
|---|---|
| `docs` | Solo documentos, diagramas o presentaciones |
| `feat` | Scripts, DDL o código (aunque también lleve documentos) |
| `fix` | Corrección de algo ya fusionado en `dev` |

---

## 5. Entrega del modelo estrella: qué commit hacer en cada fase

Dario hace dos commits en la fase 1 porque esa fase toca dos ramas suyas. En las fases 2 y 3 hace uno.

### Fase 1 · Tema, grano y cifras (se integra en EQ-02)

| Integrante | Rama | Tareas | Archivos |
|---|---|---|---|
| Dario | `feature/exploracion-bd` | DB-01, DB-03 | `etl/02_conteo_recorte.py` · `exploracion_manual/votos_por_mes.py` · `exploracion_manual/bitacora.md` |
| Dario | `docs/documentacion` | DB-02 | `docs/datos/01_exploracion_bd.md` · `docs/gestion/guia_repositorio_y_commits.md` |
| José Julio | `feature/modelo-dimensional` | JJ-01, JJ-02 | `docs/modelado/03_modelo_estrella.md` |

```bash
# Dario · feature/exploracion-bd
git add etl/02_conteo_recorte.py exploracion_manual/votos_por_mes.py exploracion_manual/bitacora.md
git commit -m "feat(fase-1): conteo real del alcance y prueba de votos acumulados" \
  -m "- DB-01: etl/02_conteo_recorte.py y las 6 cifras del alcance 2012-2013 en la bitácora.
- DB-03: exploracion_manual/votos_por_mes.py, tabla por mes y conclusión en la bitácora."
git push -u origin feature/exploracion-bd

# Dario · docs/documentacion
git add docs/datos/01_exploracion_bd.md docs/gestion/guia_repositorio_y_commits.md
git commit -m "docs(fase-1): matriz de exploración y guía del repositorio" \
  -m "- DB-02: sección Matriz de exploración en docs/datos/01_exploracion_bd.md, con las filas reales de DB-01.
- Guía de roles, ramas y commits por fase en docs/gestion/."
git push -u origin docs/documentacion

# José Julio · feature/modelo-dimensional
git add docs/modelado/03_modelo_estrella.md
git commit -m "docs(fase-1): tema del proyecto y grano de la tabla de hechos" \
  -m "- JJ-01: sección 0, Tema y proceso de negocio.
- JJ-02: sección Grano, con los granos considerados y cómo se garantiza la unicidad."
git push -u origin feature/modelo-dimensional
```

**Integración:** se abren los tres PR hacia `dev`, se revisan en EQ-02 y se fusionan.

### Fase 2 · Dimensiones, linaje y volumetría (se integra en EQ-03)

| Integrante | Rama | Tareas | Archivos |
|---|---|---|---|
| Dario | `docs/documentacion` | DB-04, DB-05 y las decisiones de EQ-02 | `docs/datos/06_linaje_plata_oro.md` · `docs/datos/01_exploracion_bd.md` · `docs/gestion/05_tareas_modelo_estrella.md` |
| José Julio | `feature/modelo-dimensional` | JJ-03, JJ-04, JJ-05 | `docs/modelado/03_modelo_estrella.md` |

```bash
# Dario · docs/documentacion
git add docs/datos/06_linaje_plata_oro.md docs/datos/01_exploracion_bd.md docs/gestion/05_tareas_modelo_estrella.md
git commit -m "docs(fase-2): linaje plata-oro y volumetría de la capa oro" \
  -m "- DB-04: docs/datos/06_linaje_plata_oro.md con origen, regla y dato faltante de cada columna de Oro.
- DB-05: sección Volumetría de Oro en docs/datos/01_exploracion_bd.md y decisión de tablas físicas.
- Decisiones de la revisión 1 y avance de la fase 1 en 05_tareas."
git push origin docs/documentacion

# José Julio · feature/modelo-dimensional
git add docs/modelado/03_modelo_estrella.md
git commit -m "docs(fase-2): dimensiones, medidas y decisiones de diseño" \
  -m "- JJ-03: fichas de las 5 dimensiones.
- JJ-04: medidas, fórmulas de KPI y KGI, y nota de votos acumulados (DB-03).
- JJ-05: decisiones de diseño y técnicas evaluadas."
git push origin feature/modelo-dimensional
```

**Integración:** dos PR hacia `dev`, revisados en EQ-03.

### Fase 3 · Validación, diagramas y presentación (se integra en EQ-04)

| Integrante | Rama | Tareas | Archivos |
|---|---|---|---|
| Dario | `docs/documentacion` | DB-06, DB-07 y las decisiones de EQ-03 | `docs/modelado/diagramas/estrella_logico.png` · `README.md` · `docs/README.md` · `docs/gestion/05_tareas_modelo_estrella.md` |
| José Julio | `feature/modelo-dimensional` | JJ-06, JJ-07, JJ-08 | `docs/modelado/03_modelo_estrella.md` · `docs/modelado/diagramas/estrella_conceptual.drawio` y `.png` · `docs/presentaciones/<entrega>.pptx` |

DB-08 no tiene commit propio: las diapositivas de Dario se le entregan a José Julio y entran en su `.pptx`.

```bash
# Dario · docs/documentacion
git add docs/modelado/diagramas/estrella_logico.png README.md docs/README.md docs/gestion/05_tareas_modelo_estrella.md
git commit -m "docs(fase-3): diagrama lógico de la estrella y readme actualizado" \
  -m "- DB-06: docs/modelado/diagramas/estrella_logico.png desde drawSQL.
- DB-07: README con el tema, el nombre completo del equipo y los documentos 04, 05 y 06.
- Decisiones de la revisión 2 y avance de las fases 2 y 3 en 05_tareas."
git push origin docs/documentacion

# José Julio · feature/modelo-dimensional
git add docs/modelado/03_modelo_estrella.md docs/modelado/diagramas/estrella_conceptual.drawio docs/modelado/diagramas/estrella_conceptual.png docs/presentaciones/
git commit -m "docs(fase-3): validación, diagrama conceptual y presentación de la entrega" \
  -m "- JJ-06: matriz de bus con la columna 'se responde con' y checklist marcado.
- JJ-07: diagrama conceptual de la estrella (.drawio y .png).
- JJ-08: presentación de la entrega con guion en las notas."
git push origin feature/modelo-dimensional
```

**Integración final (DB-09):**
1. Se fusionan los dos PR de la fase 3 en `dev`.
2. Después de EQ-04, Dario abre el PR `main` ← `dev`, José Julio lo aprueba y se fusiona.
3. Opcional: se marca la versión sustentada con `git tag entrega-modelo-estrella && git push origin entrega-modelo-estrella`.

---

## 6. Próximas entregas (propuesta, se confirma al planear cada una)

Cada entrega nueva sigue el mismo patrón:
1. Dario crea su plan y sus tareas en `docs/gestion/` (`0N_plan_<entrega>.md` y `0N_tareas_<entrega>.md`), con las tareas agrupadas en fases.
2. Cada fase cierra con un commit por rama y un PR hacia `dev`.
3. Al final, `dev` pasa a `main`.

| Entrega | Rama de Dario | Rama de José Julio |
|---|---|---|
| Arquitectura Medallion y reglas del EDA | `docs/documentacion` | `feature/modelo-dimensional` |
| Proceso ETL | `feature/etl-medallion` (`bronze/`, `silver/`, `gold/` carga, `etl/`) | Revisa los PR del ETL que tocan `gold/` |
| Visualización | `docs/documentacion` (documento final) | `feature/dashboard` (`dashboard/`) |

---

## 7. Si algo sale mal

| Situación | Solución |
|---|---|
| Agregaste un archivo que no es tuyo, antes del commit | `git restore --staged <archivo>` |
| Hiciste el commit pero no el push, y falta o sobra algo | Corrige los archivos y usa `git add <archivo>` + `git commit --amend --no-edit` |
| Trabajaste en la rama equivocada, sin commit | `git stash` · `git checkout <rama-correcta>` · `git stash pop` |
| `git push` rechazado (*non-fast-forward*) | `git pull --no-rebase origin <tu-rama>` y vuelve a hacer push |
| Conflicto al traer `dev` | Alguien editó un archivo que no era suyo. Resuelvan juntos qué versión queda y anótenlo en las decisiones de la revisión |

---

## 8. Instrucciones para Claude

Cuando Dario o José Julio digan que terminaron una fase, o pregunten qué commit hacer o en qué rama:

1. **Identifica la fase y al integrante.** Si no queda claro, pregunta solo eso.
2. **Responde con la ficha de la sección 5:**
   - Rama.
   - Comando para traer `dev` si la fase está empezando.
   - Lista exacta de archivos para `git add`.
   - Mensaje del commit (título y cuerpo).
   - `git push`.
   - PR a abrir y en qué punto de encuentro se revisa.
3. **Agrupa por fase, nunca por tarea.** Si piden un commit por tarea, recuerda la regla 2 y propón el de la fase.
4. **Revisa la propiedad de los archivos.** Si el commit incluye algo fuera del área del integrante (sección 2), adviértelo y sugiere pedírselo al dueño.
5. **No inventes rutas ni ramas.** Usa solo las de las secciones 2 y 3. Si aparece un archivo nuevo, ubícalo por su área.
6. **En entregas futuras,** aplica el mismo patrón de la sección 6 con las fases de su `0N_tareas`.
