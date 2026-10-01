"""
03_extraer_alcance_bronce.py — Extrae el alcance 2012–2013 de all.txt.gz a un CSV
listo para cargar en la capa Bronce (bronze.resenas_raw).

Qué hace:
  - Lee all.txt.gz en streaming, sin descomprimirlo a disco (regla R01).
  - Se queda con las reseñas con review/time >= 2012-01-01 00:00 UTC (regla R02).
  - Escribe los 10 campos TAL COMO VIENEN (Bronce no limpia nada): sin decodificar
    HTML, con "unknown" y con los duplicados. La limpieza es trabajo de Plata.
  - Columnas en el mismo orden y con los mismos nombres de bronze/ddl_bronze.sql.
  - Control: las filas escritas deben ser 5.627.079 (las mismas de DB-01).
  - Deja un manifiesto JSON con conteos, huella SHA-256 y cómo cargarlo.

Formato de salida: CSV UTF-8, separador coma, todos los campos entre comillas
(así un campo vacío llega a PostgreSQL como '' y no como NULL), con encabezado,
comprimido con gzip. Usa --sin-comprimir si prefieres el .csv plano.

Los datos NO van en el repositorio (GitHub no acepta archivos de GB y OneDrive
los subiría a la nube). Por defecto se guardan en ~/dw_datos/bronce/.

Uso (Git Bash):
    python etl/03_extraer_alcance_bronce.py ~/Downloads/all.txt.gz
    python etl/03_extraer_alcance_bronce.py ~/Downloads/all.txt.gz --salida ~/dw_datos/bronce --sin-comprimir
"""
import argparse
import csv
import gzip
import hashlib
import io
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

DESDE = 1325376000            # 2012-01-01 00:00:00 UTC (R02)
CONTROL_ESPERADO = 5_627_079  # reseñas del alcance medidas en DB-01
NOMBRE = "resenas_2012_2013"

# Campo de SNAP -> columna de bronze.resenas_raw (mismo orden que el DDL)
CAMPOS = {
    "product/productId": "product_id",
    "product/title": "product_title",
    "product/price": "product_price",
    "review/userId": "user_id",
    "review/profileName": "profile_name",
    "review/helpfulness": "helpfulness",
    "review/score": "score",
    "review/time": "review_time",
    "review/summary": "summary",
    "review/text": "review_text",
}
COLUMNAS = list(CAMPOS.values())


def fmt(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def main() -> None:
    p = argparse.ArgumentParser(description="Extrae el alcance 2012-2013 a CSV para Bronce")
    p.add_argument("archivo", help="ruta a all.txt.gz")
    p.add_argument("--salida", default=str(Path.home() / "dw_datos" / "bronce"),
                   help="carpeta de salida (por defecto ~/dw_datos/bronce)")
    p.add_argument("--sin-comprimir", action="store_true", help="escribir .csv en vez de .csv.gz")
    a = p.parse_args()

    entrada = Path(a.archivo).expanduser()
    carpeta = Path(a.salida).expanduser()
    carpeta.mkdir(parents=True, exist_ok=True)
    destino = carpeta / (NOMBRE + (".csv" if a.sin_comprimir else ".csv.gz"))
    parcial = destino.with_name(destino.name + ".parcial")
    manifiesto = carpeta / (NOMBRE + ".manifiesto.json")

    t0 = time.time()
    leidos = escritos = incompletos = con_nul = con_reemplazo = 0
    t_min = t_max = None
    huella = hashlib.sha256()
    buffer = io.StringIO()
    escritor = csv.writer(buffer, quoting=csv.QUOTE_ALL, lineterminator="\n")
    escritor.writerow(COLUMNAS)

    salida = (open(parcial, "wb") if a.sin_comprimir
              else gzip.open(parcial, "wb", compresslevel=6))

    def volcar() -> None:
        datos = buffer.getvalue().encode("utf-8")
        huella.update(datos)
        salida.write(datos)
        buffer.seek(0)
        buffer.truncate(0)

    reg: dict = {}

    def cerrar_registro() -> None:
        nonlocal leidos, escritos, incompletos, con_nul, con_reemplazo, t_min, t_max
        if not reg:
            return
        leidos += 1
        if leidos % 5_000_000 == 0:
            print(f"  ... {leidos // 1_000_000} M registros leídos, {fmt(escritos)} escritos "
                  f"({(time.time() - t0) / 60:.1f} min)", file=sys.stderr, flush=True)
        try:
            t = int(reg.get("review/time", ""))
        except ValueError:
            return
        if t < DESDE:
            return
        fila = []
        if len(reg) < len(CAMPOS):
            incompletos += 1
        nul = reemplazo = False
        for campo in CAMPOS:
            v = reg.get(campo, "")
            if "\x00" in v:          # PostgreSQL no admite el carácter NUL en TEXT
                v = v.replace("\x00", "")
                nul = True
            if "�" in v:
                reemplazo = True
            fila.append(v)
        con_nul += nul
        con_reemplazo += reemplazo
        escritor.writerow(fila)
        escritos += 1
        t_min = t if t_min is None or t < t_min else t_min
        t_max = t if t_max is None or t > t_max else t_max
        if escritos % 20_000 == 0:
            volcar()

    try:
        with gzip.open(entrada, "rt", encoding="utf-8", errors="replace", newline="\n") as f:
            for linea in f:
                linea = linea.rstrip("\r\n")   # solo \n separa líneas, igual que 01_exploracion.py
                if not linea:                 # línea en blanco = fin del registro
                    cerrar_registro()
                    reg = {}
                    continue
                clave, sep, valor = linea.partition(":")
                if sep and clave in CAMPOS:
                    reg[clave] = valor[1:] if valor.startswith(" ") else valor
        cerrar_registro()                     # por si el archivo no termina en línea en blanco
        volcar()
    finally:
        salida.close()

    os.replace(parcial, destino)
    segundos = time.time() - t0
    ok = escritos == CONTROL_ESPERADO
    dia = lambda ts: datetime.fromtimestamp(ts, timezone.utc).date().isoformat() if ts is not None else None

    info = {
        "archivo_origen": entrada.name,
        "bytes_origen": entrada.stat().st_size,
        "filtro": f"review/time >= {DESDE} (2012-01-01 00:00 UTC), regla R02",
        "fecha_extraccion_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "registros_leidos": leidos,
        "filas_escritas": escritos,
        "control_esperado": CONTROL_ESPERADO,
        "control_ok": ok,
        "fecha_min": dia(t_min),
        "fecha_max": dia(t_max),
        "registros_incompletos": incompletos,
        "registros_con_nul_eliminado": con_nul,
        "registros_con_utf8_reemplazado": con_reemplazo,
        "archivo": destino.name,
        "bytes_archivo": destino.stat().st_size,
        "sha256_csv_sin_comprimir": huella.hexdigest(),
        "formato": {
            "tipo": "csv", "codificacion": "utf-8", "separador": ",",
            "comillas": "todos los campos", "encabezado": True,
            "compresion": None if a.sin_comprimir else "gzip",
        },
        "columnas": COLUMNAS,
        "tabla_destino": "bronze.resenas_raw",
        "como_cargar": ("Descomprimir y en psql: \\copy bronze.resenas_raw (" + ", ".join(COLUMNAS) +
                        ") FROM '<ruta>/" + NOMBRE + ".csv' WITH (FORMAT csv, HEADER true)"),
        "segundos": round(segundos, 1),
    }
    manifiesto.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(f"Registros leídos:        {fmt(leidos)}")
    print(f"Filas escritas:          {fmt(escritos)}  -> control {fmt(CONTROL_ESPERADO)}: {'OK' if ok else 'NO COINCIDE'}")
    print(f"Rango de fechas:         {info['fecha_min']} a {info['fecha_max']}")
    print(f"Incompletos / NUL / UTF-8 reemplazado: {incompletos} / {con_nul} / {con_reemplazo}")
    print(f"Archivo:                 {destino}  ({destino.stat().st_size / 1e9:.2f} GB)")
    print(f"Manifiesto:              {manifiesto}")
    print(f"Tiempo:                  {segundos / 60:.1f} min")
    if not ok:
        sys.exit("ERROR: las filas escritas no coinciden con DB-01. No uses este archivo; revisa el filtro.")


if __name__ == "__main__":
    main()
