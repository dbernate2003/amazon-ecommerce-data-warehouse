"""
02_conteo_recorte.py — Volumetría real del alcance 2012–2013.

Recorre all.txt.gz en streaming (sin descomprimirlo a disco) y cuenta, solo para
las reseñas con review/time >= 2012-01-01 00:00 UTC:
  - reseñas del alcance (control: debe dar 5.627.079)
  - productos distintos  -> filas de dim_producto
  - clientes distintos   -> filas de dim_cliente (sin contar los anónimos)
  - reseñas anónimas     -> van a cliente_sk = -2
  - días distintos con reseñas

Uso:
    python etl/02_conteo_recorte.py "C:/Users/<usuario>/Downloads/all.txt.gz"
"""
import gzip
import sys
import time
from datetime import datetime, timezone

DESDE = 1325376000  # 2012-01-01 00:00:00 UTC
CLAVES = ("product/productId", "review/userId", "review/time")


def main(archivo: str) -> None:
    t0 = time.time()
    total = resenas = anonimas = 0
    productos, clientes, dias = set(), set(), set()
    reg = {}

    def cerrar_registro() -> None:
        nonlocal total, resenas, anonimas
        if not reg:
            return
        total += 1
        if total % 5_000_000 == 0:  # avance cada 5 M registros
            print(f"  ... {total // 1_000_000} M registros leídos ({(time.time() - t0) / 60:.1f} min)", flush=True)
        try:
            t = int(reg.get("review/time", "-1"))
        except ValueError:
            t = -1
        if t < DESDE:
            return
        resenas += 1
        productos.add(reg.get("product/productId"))
        dias.add(datetime.fromtimestamp(t, timezone.utc).date())
        usuario = reg.get("review/userId", "unknown")
        if usuario == "unknown":
            anonimas += 1
        else:
            clientes.add(usuario)

    with gzip.open(archivo, "rt", encoding="utf-8", errors="replace") as f:
        for linea in f:
            linea = linea.rstrip("\r\n")
            if not linea:  # línea en blanco = fin del registro
                cerrar_registro()
                reg = {}
                continue
            clave, _, valor = linea.partition(": ")
            if clave in CLAVES:
                reg[clave] = valor
    cerrar_registro()  # por si el archivo no termina en línea en blanco

    minutos = (time.time() - t0) / 60
    print(f"Registros leídos (todo el archivo): {total:,}".replace(",", "."))
    print(f"Reseñas del alcance 2012-2013:      {resenas:,}".replace(",", "."))
    print(f"Productos distintos (dim_producto): {len(productos):,}".replace(",", "."))
    print(f"Clientes distintos (dim_cliente):   {len(clientes):,}".replace(",", "."))
    print(f"Reseñas anónimas (cliente_sk = -2): {anonimas:,}".replace(",", "."))
    if resenas:
        print(f"% anónimas en el alcance:           {anonimas / resenas * 100:.1f} %".replace(".", ","))
    print(f"Días distintos con reseñas:         {len(dias):,}".replace(",", "."))
    print(f"Tiempo: {minutos:.1f} min".replace(".", ","))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit('Uso: python etl/02_conteo_recorte.py "ruta/a/all.txt.gz"')
    main(sys.argv[1])
