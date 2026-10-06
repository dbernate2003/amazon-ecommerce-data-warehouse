# Capa Bronce — cargar la historia de 3 años en PostgreSQL

Esta guía deja lista la **capa Bronce** del proyecto en tu PostgreSQL local: la base `dws_amazon` con la tabla `raw.reviews`, que guarda **9.707.634 reseñas de Amazon publicadas entre el 2010-03-04 y el 2013-03-04 (UTC)**.

---

## 1. Qué es la capa Bronce

En la arquitectura Medallón cada capa tiene un trabajo:

| Capa | Esquema | Qué guarda |
|---|---|---|
| **Bronce** | `raw` | El dato **tal como viene del archivo**, sin limpiar ni corregir |
| Plata | `silver` | El dato limpio y normalizado (producto, cliente, reseña) |
| Oro | `gold` | El modelo estrella para el análisis en Tableau |

Bronce **no se modifica nunca**. Si una regla de limpieza de Plata sale mal, se vuelve a procesar desde Bronce sin tener que leer otra vez el archivo de 11 GB.

### De dónde salen los datos

| | Archivo | Reseñas | Periodo |
|---|---|---:|---|
| Fuente original (SNAP, Stanford) | `all.txt.gz` (11 GB) | 34.686.770 | 1995 – 2013 |
| **Historia del proyecto** | `all_3y.txt.gz` | **9.707.634** | **2010-03-04 – 2013-03-04** |

Los 3 años se cuentan hacia atrás desde la **última fecha del dataset** (2013-03-04), no desde hoy. El archivo `all_3y.txt.gz` ya trae ese recorte: solo hay que descargarlo y cargarlo.

### Ruta de la carga

```
all_3y.txt.gz ──► all_3y_pipe.txt ──► raw.reviews ──► validación
 (descargar)       (Git Bash, paso 4)   (psql, paso 6)   (pgAdmin, paso 7)
```

PostgreSQL no lee archivos `.gz`, y el archivo original no es una tabla: cada reseña ocupa 10 líneas. Por eso primero se convierte a **una línea por reseña** y después se carga.

---

## 2. Requisitos

| Necesitas | Para qué |
|---|---|
| **PostgreSQL** (el proyecto usa la versión 18) y **pgAdmin 4** | La base de datos. Anota la contraseña del usuario `postgres` |
| **Git for Windows** | Trae **Git Bash** con `gzip`, `awk` y `cygpath` |
| **≈ 25 GB libres** | El `.gz` descargado, el archivo intermedio (≈ 6,2 GB) y la base |

Abre **Git Bash** y revisa las herramientas:

```bash
awk --version | head -1     # debe mostrar la versión de awk
psql --version              # debe mostrar la versión de PostgreSQL
```

Si `psql` dice `command not found`, no pasa nada: en el paso 6 se usa su ruta completa.

### Reglas para Git Bash

1. **Los comandos no muestran avance.** Leen millones de líneas y tardan varios minutos. Espera a que vuelva el prompt `$` y **no pulses Ctrl+C**.
2. **Pega cada bloque completo de una vez.**
3. **Si queda un prompt `>`**, faltó cerrar una comilla. Pulsa Ctrl+C y vuelve a copiar el bloque.

---

## 3. Descargar el archivo

**Enlace:** [all_3y.txt.gz en Google Drive](https://drive.google.com/file/d/1dVqJwi9sNDR5F4loD8RS0QaYlkMnFGYD/view?usp=drive_link)

Guárdalo en tu carpeta **Descargas** con el nombre `all_3y.txt.gz`. Si queda con otro nombre (por ejemplo `all_3y (1).txt.gz`), cámbialo o ajusta la variable `G` de los pasos siguientes.

Comprueba que llegó completo:

```bash
G=~/Downloads/all_3y.txt.gz

ls -lh "$G"
gzip -t "$G" && echo "gz íntegro"
gzip -dc "$G" | grep -c "^product/productId:"
```

| Debe salir | Si no sale |
|---|---|
| `gz íntegro` | El archivo se descargó incompleto: descárgalo otra vez |
| `9707634` | No es el archivo del proyecto: descárgalo otra vez |

---

## 4. Convertir el archivo a una línea por reseña

En el archivo, cada reseña ocupa 10 líneas (una por campo) y las reseñas se separan con una línea en blanco:

```
product/productId: B000O1UCCQ
product/title: ...
product/price: unknown
review/userId: A2MPRPCAQLTR3L
review/profileName: Judith Land "Adoption Detective | First Lilac..."
review/helpfulness: 1/2
review/score: 5.0
review/time: 1267660800
review/summary: ...
review/text: ...
```

Este bloque junta cada reseña en **una sola línea con los 10 campos separados por `|`**. Como algunos textos traen `|` o `\` adentro, los **escapa** (les pone un `\` delante) para que PostgreSQL no los confunda con el separador:

```bash
G=~/Downloads/all_3y.txt.gz
TXT=~/Downloads/all_3y_pipe.txt

gzip -dc "$G" | LC_ALL=C awk '
BEGIN { RS=""; FS="\n"; OFS="|" }
{
  delete r
  for (i = 1; i <= NF; i++) {
    p = index($i, ":")
    if (p == 0) continue
    k = substr($i, 1, p-1)
    v = substr($i, p+1); sub(/^ /, "", v)
    gsub(/\r/, "", v)
    gsub(/\\/, "\\\\&", v)
    gsub(/\|/, "\\\\&", v)
    r[k] = v
  }
  print r["product/productId"], r["product/title"], r["product/price"],
        r["review/userId"], r["review/profileName"], r["review/helpfulness"],
        r["review/score"], r["review/time"], r["review/summary"], r["review/text"]
}' > "$TXT"

ls -lh "$TXT"
wc -l "$TXT"
```

**Debe salir:** un archivo de unos 6,2 GB y `wc -l` igual a **9707634** (una línea por reseña).

Qué hace cada parte, por si te lo preguntan:

| Parte | Qué hace |
|---|---|
| `RS=""` | Toma como un registro todo lo que hay entre dos líneas en blanco (una reseña) |
| `FS="\n"` | Cada línea del registro es un campo (`product/title: ...`) |
| `index($i, ":")` | Separa el nombre del campo de su valor en el primer `:` |
| `gsub(/\r/ ...)` | Quita retornos de carro de Windows |
| Los dos `gsub` siguientes | Ponen un `\` delante de cada `\` y de cada barra vertical que venga dentro del texto |
| `print ... OFS="\|"` | Escribe los 10 valores en orden, separados por `\|` |

> Si el bloque se pega cortado, guárdalo en un archivo `convertir.sh` (en VS Code, cambia el fin de línea de `CRLF` a `LF`, abajo a la derecha) y ejecútalo con `bash convertir.sh`.

### Comprobar el formato antes de cargar

Este comando busca líneas que **no** tengan exactamente 10 campos:

```bash
LC_ALL=C grep -n -v -E -m 5 '^([^|\\]|\\.)*(\|([^|\\]|\\.)*){9}$' "$TXT" | cut -c1-400
```

**No debe imprimir nada.** Si imprime líneas, no cargues el archivo: repite el paso 4.

---

## 5. Crear la base de datos y la tabla (pgAdmin)

1. Abre **pgAdmin 4**, expande **Servers** y entra con la contraseña de `postgres`.
2. Clic derecho en **Databases** → **Create** → **Database...** → nombre `dws_amazon`, owner `postgres` → **Save**.
3. Selecciona `dws_amazon` y abre **Tools** → **Query Tool**. Revisa que la pestaña diga `dws_amazon/postgres@...`.
4. Ejecuta (▶ o F5):

```sql
CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.reviews (
    product_id    TEXT,      -- product/productId
    title         TEXT,      -- product/title
    price         TEXT,      -- product/price: 'unknown' en muchos casos
    user_id       TEXT,      -- review/userId: 'unknown' = reseña anónima
    profile_name  TEXT,      -- review/profileName
    helpfulness   TEXT,      -- review/helpfulness: formato '3/5'
    score         TEXT,      -- review/score: formato '5.0'
    review_time   BIGINT,    -- review/time: segundos desde 1970 (epoch), UTC
    summary       TEXT,      -- review/summary
    review_text   TEXT       -- review/text
);

COMMENT ON TABLE raw.reviews IS
    'Capa Bronce: reseñas de Amazon (SNAP) del 2010-03-04 al 2013-03-04 (UTC), sin transformar';
```

**Por qué casi todo es `TEXT`:** Bronce guarda el dato tal cual. Si `price` fuera numérico, la carga fallaría con `unknown`. La única excepción es `review_time`, que siempre es un número entero (epoch) y así se puede filtrar y validar. Convertirlo a fecha se hace en Plata.

5. Comprueba la estructura (deben salir **10 filas**):

```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'raw' AND table_name = 'reviews'
ORDER BY ordinal_position;
```

---

## 6. Cargar el archivo en la tabla (Git Bash)

La carga se hace con `psql` y el comando `\copy`, que lee el archivo desde tu PC y deja escrito el separador `|` en el propio comando.

```bash
PSQL="/c/Program Files/PostgreSQL/18/bin/psql.exe"    # cambia 18 por tu versión
TXT=~/Downloads/all_3y_pipe.txt
TXTW=$(cygpath -m "$TXT")                              # ruta en formato C:/Users/...

"$PSQL" -U postgres -d dws_amazon -c "\copy raw.reviews FROM '$TXTW' WITH (FORMAT text, DELIMITER '|', ENCODING 'UTF8')"
```

- Pide `Password for user postgres:`. Al escribir no se ve nada; es normal. Pulsa Enter.
- Tarda varios minutos y no muestra avance.
- **Debe terminar con `COPY 9707634`.**
- Es todo o nada: si falla, no queda ninguna fila y el mensaje dice en qué línea.

`\copy` es un comando de `psql`, no de SQL: **no funciona en el Query Tool de pgAdmin**.

---

## 7. Validar la carga (pgAdmin)

En el Query Tool de `dws_amazon`:

```sql
SELECT count(*)                                          AS registros,
       min(review_time)                                  AS epoch_min,
       max(review_time)                                  AS epoch_max,
       to_timestamp(min(review_time)) AT TIME ZONE 'UTC' AS desde_utc,
       to_timestamp(max(review_time)) AT TIME ZONE 'UTC' AS hasta_utc
FROM raw.reviews;
```

| Campo | Debe dar |
|---|---|
| `registros` | **9707634** |
| `epoch_min` | **1267660800** |
| `epoch_max` | **1362355200** |
| `desde_utc` | **2010-03-04 00:00:00** |
| `hasta_utc` | **2013-03-04 00:00:00** |

> **Sobre la zona horaria.** Sin `AT TIME ZONE 'UTC'`, pgAdmin muestra la hora de Colombia: `2010-03-03 19:00:00-05`. Es el mismo instante, pero en otro día del calendario. Por eso todas las fechas del proyecto se convierten en UTC.

### Comprobar que el escape funcionó

Este perfil tiene un `|` dentro del nombre:

```sql
SELECT profile_name
FROM raw.reviews
WHERE product_id = 'B000O1UCCQ' AND user_id = 'A2MPRPCAQLTR3L'
LIMIT 1;
```

Debe salir `Judith Land "Adoption Detective | First Lilac...`, con **una sola** barra vertical y **sin** `\`.

---

## 8. Limpieza

Cuando la validación dé bien, borra el archivo intermedio de 6,2 GB. **Conserva el `.gz`**: es la copia de respaldo de Bronce.

```bash
rm ~/Downloads/all_3y_pipe.txt
```

---

## 9. Si algo falla

| Síntoma | Causa y solución |
|---|---|
| `psql: command not found` | `psql` no está en el PATH. Usa la ruta completa del paso 6 |
| `No such file or directory` con `psql.exe` | Tu versión no es la 18. Mira el nombre de la carpeta en `C:\Program Files\PostgreSQL\` |
| `password authentication failed` | La contraseña no es la del usuario `postgres` |
| `invalid byte sequence for encoding "UTF8": 0x8b` | Se intentó importar el `.gz`. Importa el `.txt` del paso 4 |
| `missing data for column "review_time"` | El separador quedó como `,`. Debe ser `\|` |
| `extra data after last expected column` | Hay líneas con más de 10 campos. Repite el paso 4 y el `grep` de formato |
| `relation "raw.reviews" already exists` | La tabla ya existía. Revisa con `SELECT count(*) FROM raw.reviews;` |
| El conteo da el doble | Se cargó dos veces. Ejecuta `TRUNCATE raw.reviews;` y repite el paso 6 |
| Un comando termina en `>` | Quedó una comilla abierta. Ctrl+C y copia el bloque otra vez |
| Poco espacio en disco | Usa la variante del paso 10 |

**No uses un CSV ni el asistente Import/Export de pgAdmin.** En el proyecto se probaron y fallaron: el texto de las reseñas trae comas, comillas y saltos que rompen el CSV.

---

## 10. Variante sin archivo intermedio (si te falta espacio)

Convierte y carga en un solo paso, sin crear los 6,2 GB. La desventaja es que no se puede revisar el formato antes; si algo falla, `\copy` no carga nada y dice la línea.

```bash
G=~/Downloads/all_3y.txt.gz
PSQL="/c/Program Files/PostgreSQL/18/bin/psql.exe"    # cambia 18 por tu versión
export PGPASSWORD='TU_CONTRASEÑA_DE_POSTGRES'

gzip -dc "$G" | LC_ALL=C awk '
BEGIN { RS=""; FS="\n"; OFS="|" }
{
  delete r
  for (i = 1; i <= NF; i++) {
    p = index($i, ":")
    if (p == 0) continue
    k = substr($i, 1, p-1)
    v = substr($i, p+1); sub(/^ /, "", v)
    gsub(/\r/, "", v)
    gsub(/\\/, "\\\\&", v)
    gsub(/\|/, "\\\\&", v)
    r[k] = v
  }
  print r["product/productId"], r["product/title"], r["product/price"],
        r["review/userId"], r["review/profileName"], r["review/helpfulness"],
        r["review/score"], r["review/time"], r["review/summary"], r["review/text"]
}' | "$PSQL" -U postgres -d dws_amazon -c "\copy raw.reviews FROM STDIN WITH (FORMAT text, DELIMITER '|', ENCODING 'UTF8')"

unset PGPASSWORD
```

Debe terminar con `COPY 9707634`. Después valida con el paso 7.

---

## Siguiente paso

Con `raw.reviews` cargada y validada, sigue la **capa Plata**: `silver/ddl_silver.sql` y `silver/etl_silver.sql`.
