# Bitácora de exploración manual

Registro de las pruebas sobre los datos: comando, cifras, controles y conclusión. Responsable: Dario (Data Engineer).

> **Cambio de alcance (3 oct 2026).** Por recomendación del profesor, la historia pasa a los **últimos 3 años del dataset: 2010-03-04 a 2013-03-04 (UTC), 9.707.634 reseñas**, cargadas en `raw.reviews` (PostgreSQL). Las pruebas con el alcance anterior (enero 2012 – marzo 2013) quedan como evidencia en [`bitacora_alcance_original.md`](bitacora_alcance_original.md). Sus scripts se renombraron: `etl/02_conteo_recorte.py` → `etl/02_conteo_recorte_alcance_original.py` y `exploracion_manual/votos_por_mes.py` → `exploracion_manual/votos_por_mes_alcance_original.py`.

---

## DB-01 · Conteo real del alcance · 2026-10-03

### Reducción de la historia

Fecha máxima del archivo y fecha de corte (Git Bash):

```bash
F=~/Downloads/all.txt.gz
MAX=$(gzip -dc "$F" | awk '/^review\/time:/ { if ($2+0 > m) m = $2+0 } END { print m }')
CUT=$(date -u -d "$(date -u -d @$MAX '+%Y-%m-%d') - 3 years" +%s)
```

| Dato | Valor |
|---|---|
| Fecha máxima | 1362355200 → 2013-03-04 |
| Fecha de corte | 1267660800 → 2010-03-04 |

Archivo intermedio con la ventana de 3 años:

```bash
OUT=~/Downloads/all_3y.txt.gz
gzip -dc "$F" | awk -v cut="$CUT" '
BEGIN { RS=""; FS="\n"; ORS="\n\n" }
{
  t = 0
  for (i = 1; i <= NF; i++)
    if ($i ~ /^review\/time: /) { t = substr($i, 14) + 0; break }
  if (t >= cut) print
}' | gzip -6 > "$OUT"
gzip -t "$OUT" && echo "gz íntegro"
```

### Controles de la carga

| Control | Valor | Resultado |
|---|---:|---|
| `gzip -t` sobre `all_3y.txt.gz` | — | ✔ gz íntegro |
| Registros en `all_3y.txt.gz` | 9.707.634 | ✔ |
| Filas cargadas en `raw.reviews` (`COPY`) | 9.707.634 | ✔ Igual al archivo intermedio |
| Rango de fechas en `raw.reviews` | ⟨desde⟩ a ⟨hasta⟩ | Debe dar 2010-03-04 a 2013-03-04 |
| Peso de `all_3y.txt.gz` | ⟨ ⟩ | — |

### Cifras del alcance (bloque 3 de `db02_db03_perfilado_raw.sql`)

| Cifra | Valor | Control |
|---|---:|---|
| **Reseñas del alcance** | **9.707.634** | Debe coincidir con el `COPY` ⟨✔ / ✘⟩ |
| Productos distintos → `silver.producto` | ⟨ ⟩ | ≤ 2.441.053 (todo el dataset) |
| Clientes distintos → `silver.cliente` | ⟨ ⟩ | ≤ 6.643.669 (todo el dataset) |
| Reseñas anónimas → `cliente_sk = -2` | ⟨ ⟩ | — |
| % de anónimas en el alcance | ⟨ ⟩ % | 14,5 % en todo el dataset |
| Días distintos con reseñas | ⟨ ⟩ | 1.097 si hubo reseñas todos los días (2010-03-04 a 2013-03-04) |
| Tiempo de ejecución (pgAdmin) | ⟨ ⟩ | — |

Filas de Oro que salen de aquí:
- `dim_producto` = productos + 1 (fila -1 "Desconocido") = ⟨ ⟩
- `dim_cliente` = clientes + 2 (filas -1 "Desconocido" y -2 "Anónimo") = ⟨ ⟩
- `dim_fecha` = 1.462 (calendario 2010–2013 completo, 1.461 días, + fila -1).

---

## DB-03 · Prueba de votos acumulados · ⟨fecha⟩

Consulta: bloque 6 de `db02_db03_perfilado_raw.sql`, sobre las 9.707.634 reseñas de `raw.reviews`.

⟨pega aquí la tabla por mes y el resumen por año⟩

**Conclusión:**
1. Los votos ⟨SÍ / NO⟩ son acumulados: el % de reseñas con votos pasa de ⟨X⟩ % en 2010-03 a ⟨Y⟩ % en 2013-02, y baja ⟨mes a mes / sin patrón⟩.
2. El % útiles ⟨se mantiene entre A % y B % / cambia de A % a B %⟩, así que la proporción ⟨sí / no⟩ se puede comparar entre meses.
3. Para el análisis (JJ-04): ⟨qué medida de utilidad se usa y qué no se compara entre meses⟩.
