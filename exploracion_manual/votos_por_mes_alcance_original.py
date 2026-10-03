"""
votos_por_mes.py — Prueba de votos acumulados (tarea DB-03).

Pregunta que responde: ¿las reseñas más recientes tienen menos votos de utilidad
solo porque tuvieron menos tiempo para recibirlos?

Lee reseñas en el formato de SNAP (bloques "campo: valor" separados por una línea
en blanco), se queda con el alcance (review/time >= 2012-01-01 00:00 UTC) y, por
cada mes, calcula:
  - Reseñas           cuántas reseñas tiene el mes
  - % con votos       reseñas con votos_totales > 0 / reseñas
  - Votos por reseña  SUM(votos_totales) / reseñas
  - % útiles          SUM(votos_utiles) / SUM(votos_totales)   (misma fórmula del KPI)

Aplica R06 (separar "a/b") y R07 (si útiles > totales, útiles = totales).
La salida es una tabla Markdown lista para pegar en la bitácora.

Uso (Git Bash):
    python exploracion_manual/votos_por_mes.py ~/Downloads/muestra_1pct.txt
    python exploracion_manual/votos_por_mes.py ~/Downloads/all.txt.gz      # cifras finales
    gzip -dc "$F" | python exploracion_manual/votos_por_mes.py -             # igual, por tubería
"""
import gzip
import io
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone

DESDE = 1325376000          # 2012-01-01 00:00:00 UTC (regla R02)
MIN_ESTABLE = 1000          # por debajo de esto, la cifra del mes es poco estable
NOMBRE_MES_PARCIAL = {"2013-03": "2013-03 (1-4 mar)"}  # el archivo termina el 2013-03-04


def abrir(ruta: str):
    """Devuelve un iterador de líneas de texto para un .gz, un .txt o stdin ('-')."""
    if ruta == "-":
        return io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")
    if ruta.lower().endswith(".gz"):
        return gzip.open(ruta, "rt", encoding="utf-8", errors="replace")
    return open(ruta, "r", encoding="utf-8", errors="replace")


def fmt_int(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def fmt_dec(x: float, dec: int = 1) -> str:
    return f"{x:.{dec}f}".replace(".", ",")


def main(ruta: str) -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    t0 = time.time()

    # por mes: [reseñas, con_votos, suma_utiles, suma_totales]
    meses = defaultdict(lambda: [0, 0, 0, 0])
    leidos = invalidos = acotados = 0
    tiempo = votos = None

    def cerrar() -> None:
        nonlocal leidos, invalidos, acotados
        if tiempo is None and votos is None:
            return
        leidos += 1
        if leidos % 5_000_000 == 0:
            print(f"  ... {leidos // 1_000_000} M registros leídos "
                  f"({fmt_dec((time.time() - t0) / 60)} min)", file=sys.stderr, flush=True)
        try:
            t = int(tiempo)
        except (TypeError, ValueError):
            return
        if t < DESDE:
            return
        try:
            a, b = (int(p) for p in votos.split("/"))
        except (AttributeError, ValueError):
            invalidos += 1
            return
        if a > b:                      # R07
            a = b
            acotados += 1
        mes = datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m")
        m = meses[mes]
        m[0] += 1
        m[1] += 1 if b > 0 else 0
        m[2] += a
        m[3] += b

    with abrir(ruta) as f:
        for linea in f:
            linea = linea.rstrip("\r\n")
            if not linea:
                cerrar()
                tiempo = votos = None
                continue
            if linea.startswith("review/time:"):
                tiempo = linea.partition(": ")[2]
            elif linea.startswith("review/helpfulness:"):
                votos = linea.partition(": ")[2]
    cerrar()

    total_alcance = sum(m[0] for m in meses.values())
    print(f"Fuente: {ruta}")
    print(f"Registros leídos: {fmt_int(leidos)} | Reseñas del alcance: {fmt_int(total_alcance)} | "
          f"helpfulness inválido: {fmt_int(invalidos)} | acotados por R07: {fmt_int(acotados)}")
    if not total_alcance:
        print("\nLa entrada no tiene reseñas desde 2012-01-01. "
              "Corre el script sobre all.txt.gz para obtener la tabla.")
        return

    def fila(etiqueta: str, m: list) -> str:
        r, cv, u, tot = m
        pct_votos = cv / r * 100
        votos_res = tot / r
        pct_utiles = fmt_dec(u / tot * 100) + " %" if tot else "—"
        marca = " (*)" if r < MIN_ESTABLE else ""
        return (f"| {etiqueta}{marca} | {fmt_int(r)} | {fmt_dec(pct_votos)} % | "
                f"{fmt_dec(votos_res, 2)} | {pct_utiles} |")

    print()
    print("| Mes | Reseñas | % con votos | Votos por reseña | % útiles |")
    print("|---|---:|---:|---:|---:|")
    for mes in sorted(meses):
        print(fila(NOMBRE_MES_PARCIAL.get(mes, mes), meses[mes]))

    anios = defaultdict(lambda: [0, 0, 0, 0])
    for mes, m in meses.items():
        acumulado = anios[mes[:4]]
        for i in range(4):
            acumulado[i] += m[i]
    for anio in sorted(anios):
        print(fila(f"**Total {anio}**", anios[anio]))
    todo = [sum(m[i] for m in meses.values()) for i in range(4)]
    print(fila("**Alcance**", todo))

    if any(m[0] < MIN_ESTABLE for m in meses.values()):
        print(f"\n(*) Menos de {fmt_int(MIN_ESTABLE)} reseñas en el mes: la cifra es poco estable.")

    # Comparación rápida: primer mes contra el último mes completo del alcance
    completos = [m for m in sorted(meses) if m != "2013-03"]
    if len(completos) >= 2:
        ini, fin = completos[0], completos[-1]
        mi, mf = meses[ini], meses[fin]
        pv_i, pv_f = mi[1] / mi[0] * 100, mf[1] / mf[0] * 100
        print(f"\nComparación {ini} → {fin}:")
        print(f"  % con votos:      {fmt_dec(pv_i)} % → {fmt_dec(pv_f)} % "
              f"({fmt_dec(pv_f - pv_i)} puntos)")
        print(f"  Votos por reseña: {fmt_dec(mi[3] / mi[0], 2)} → {fmt_dec(mf[3] / mf[0], 2)}")
        if mi[3] and mf[3]:
            pu_i, pu_f = mi[2] / mi[3] * 100, mf[2] / mf[3] * 100
            print(f"  % útiles:         {fmt_dec(pu_i)} % → {fmt_dec(pu_f)} % "
                  f"({fmt_dec(pu_f - pu_i)} puntos)")

    print(f"\nTiempo: {fmt_dec((time.time() - t0) / 60)} min")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit('Uso: python exploracion_manual/votos_por_mes.py "ruta/a/muestra_o_all.txt.gz"  (o "-" para leer de la tubería)')
    main(sys.argv[1])
