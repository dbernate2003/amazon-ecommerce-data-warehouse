# Bitácora de exploración manual

Registro de las pruebas sobre los datos: comando, cifras, controles y conclusión. Responsable: Dario (Data Engineer).

---

## DB-01 · Conteo real del alcance · 2026-09-30

Comando:

```bash
F=~/Downloads/all.txt.gz
time PYTHONIOENCODING=utf-8 python etl/02_conteo_recorte.py "$F" | tee ~/Downloads/salida_db01.txt
```

| Cifra | Valor | Control |
|---|---:|---|
| Registros leídos (todo el archivo) | 34.686.770 | ✔ Igual a `total_registros` de `docs/datos/perfil_dataset.json` |
| **Reseñas del alcance 2012–2013** | **5.627.079** | ✔ Igual a 3.856.226 (2012) + 1.770.853 (2013) de `por_anio` |
| Productos distintos → `silver.producto` | 892.006 | ✔ ≤ 2.441.053 (36,5 % de los productos del dataset) |
| Clientes distintos → `silver.cliente` | 1.738.966 | ✔ ≤ 6.643.669 (26,2 % de los usuarios del dataset) |
| Reseñas anónimas → `cliente_sk = -2` | 5.382 | — |
| % de anónimas en el alcance | 0,1 % | ⚠ En todo el dataset es 14,5 % (ver observaciones) |
| Días distintos con reseñas | 429 | ✔ Hubo reseñas todos los días del 2012-01-01 al 2013-03-04 |
| Tiempo de ejecución (`real` de `time`) | 5 min 42 s | — |

Filas de Oro que salen de aquí:
- `dim_producto` = 892.006 + 1 (fila -1 "Desconocido") = **892.007**
- `dim_cliente` = 1.738.966 + 2 (filas -1 "Desconocido" y -2 "Anónimo") = **1.738.968**
- `dim_fecha` = 732 (calendario 2012–2013 completo + fila -1); de esos días, 429 tienen reseñas.

Cifras derivadas:
- Reseñas con cliente identificado: 5.627.079 − 5.382 = 5.621.697.
- Reseñas por cliente identificado: 5.621.697 / 1.738.966 ≈ 3,2.
- Reseñas por producto: 5.627.079 / 892.006 ≈ 6,3.

**Observaciones:**
1. **Los dos controles coinciden.** El filtro R02 (`review/time >= 1325376000`) selecciona exactamente las reseñas que la exploración clasificó como 2012 y 2013, y el archivo se leyó completo.
2. **Las reseñas anónimas casi desaparecen en el alcance: 0,1 %, frente al 14,5 % del dataset completo.** La fila -2 "Anónimo" se mantiene, pero solo recibe 5.382 reseñas. Hay que revisar los textos que usan el 14,5 % como dato del alcance: plan, sección 4; `03_modelo_estrella.md`; KPI "% reseñas anónimas" y RQ-11.
3. **Las dimensiones de Plata y Oro son mucho menores que las cotas de `01_exploracion_bd.md`:** 0,89 M productos en vez de 2,44 M, y 1,74 M clientes en vez de 6,64 M. DB-05 debe usar estas cifras.

---

## DB-03 · Prueba de votos acumulados · 2026-09-30

Comando (archivo completo, sin muestra: tarda lo mismo que DB-01):

```bash
python exploracion_manual/votos_por_mes.py "$F" | tee ~/Downloads/salida_db03.txt
```

Entrada: `all.txt.gz` · 34.686.770 registros leídos · 5.627.079 reseñas del alcance · `helpfulness` inválido: 0 · acotados por R07: 0 (los 86 casos del dataset caen fuera del alcance) · 5,4 min

| Mes | Reseñas | % con votos | Votos por reseña | % útiles |
|---|---:|---:|---:|---:|
| 2012-01 | 274.880 | 50,1 % | 1,76 | 58,0 % |
| 2012-02 | 214.049 | 49,6 % | 1,81 | 58,1 % |
| 2012-03 | 238.241 | 47,6 % | 1,64 | 58,5 % |
| 2012-04 | 214.500 | 45,9 % | 1,53 | 58,9 % |
| 2012-05 | 216.291 | 46,0 % | 1,47 | 57,5 % |
| 2012-06 | 213.124 | 42,8 % | 1,36 | 57,6 % |
| 2012-07 | 234.142 | 40,1 % | 1,18 | 58,3 % |
| 2012-08 | 236.226 | 37,6 % | 1,13 | 57,6 % |
| 2012-09 | 323.663 | 32,6 % | 0,92 | 55,2 % |
| 2012-10 | 337.045 | 29,5 % | 0,84 | 56,0 % |
| 2012-11 | 459.391 | 25,3 % | 0,54 | 54,4 % |
| 2012-12 | 894.674 | 20,0 % | 0,36 | 54,0 % |
| 2013-01 | 1.037.101 | 14,2 % | 0,23 | 55,5 % |
| 2013-02 | 708.975 | 7,8 % | 0,12 | 53,0 % |
| 2013-03 (1-4 mar) | 24.777 | 3,6 % | 0,05 | 53,0 % |
| **Total 2012** | 3.856.226 | 34,5 % | 1,01 | 57,2 % |
| **Total 2013** | 1.770.853 | 11,5 % | 0,18 | 54,8 % |
| **Alcance** | 5.627.079 | 27,2 % | 0,75 | 57,0 % |

Control cruzado: las reseñas por mes coinciden con la tabla mensual de `docs/datos/01_exploracion_bd.md`, sección 3.

**Conclusión:**
1. **Los votos SÍ son acumulados.** El % de reseñas con votos baja mes a mes, de 50,1 % en 2012-01 a 7,8 % en 2013-02, y los votos por reseña caen de 1,76 a 0,12. La caída ya es continua entre enero y noviembre de 2012 (50,1 % → 25,3 %), antes del pico de diciembre, así que se debe al tiempo que tuvo cada reseña para recibir votos y no al cambio de volumen.
2. **El % útiles se mantiene en una franja estrecha:** entre 53,0 % y 58,9 %. Baja 5 puntos (58,0 % → 53,0 %), frente a 42 puntos del % con votos. La proporción sí se puede comparar entre meses, con cautela de diciembre 2012 a marzo 2013, que tienen pocas reseñas votadas.
3. **Para el análisis (JJ-04):** no comparar entre meses votos absolutos, % de reseñas con votos ni el rango "Sin votos". La utilidad se mide con % útiles = SUM(votos_utiles) / SUM(votos_totales), con una nota en el dashboard sobre los meses recientes.

**Observaciones para el diseño:**
- En el alcance, el **72,8 % de las reseñas no tiene votos** (100 % − 27,2 %), frente al 32,2 % del dataset completo. `utilidad_sk = 0` "Sin votos" será la fila más usada de `dim_utilidad`.
- El % útiles real del alcance es **57,0 %**. La meta de referencia del KGI Confianza (≥ 70 %, en `00_planteamiento.md`) queda lejos; conviene revisarla en JJ-04.
