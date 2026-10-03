"""
01_exploracion.py — Exploración (profiling) del dataset de reseñas de Amazon.

Formato real del archivo (verificado sobre una muestra):
    Cada registro es un bloque de líneas "clave: valor" separado por una línea vacía.

        product/productId: B000GKXY34
        product/title: Nun Chuck, Novelty Nun Toss Toy
        product/price: 17.99
        review/userId: ADX8VLDUOL7BG
        review/profileName: M. Gingras
        review/helpfulness: 0/0
        review/score: 5.0
        review/time: 1262304000
        review/summary: Great fun!
        review/text: Got these last Christmas as a gag gift. ...

El archivo se lee en streaming desde el .gz: nunca se descomprime a disco ni se
carga completo en memoria. Para contar distintos y duplicados sobre ~60M de
registros se guardan solo hashes de 64 bits en archivos temporales particionados
(se borran al terminar).

Uso:
    python etl/01_exploracion.py --archivo "C:/Users/Dario/Downloads/all.txt.gz"
    python etl/01_exploracion.py --archivo ... --limite 100000        # prueba rápida
    python etl/01_exploracion.py --archivo ... --salida docs/datos/perfil_dataset.json
"""

import argparse
import collections
import gzip
import json
import os
import re
import sys
import tempfile
import time
from array import array

# Campos observados en el archivo. Se usan para detectar faltantes; cualquier
# otra clave que aparezca se registra igualmente como "campo inesperado".
CAMPOS_ESPERADOS = [
    "product/productId",
    "product/title",
    "product/price",
    "review/userId",
    "review/profileName",
    "review/helpfulness",
    "review/score",
    "review/time",
    "review/summary",
    "review/text",
]
CAMPO_INICIO = "product/productId"

RE_CLAVE = re.compile(r"^([A-Za-z]+/[A-Za-z]+):(?: (.*))?$")
RE_ENTERO = re.compile(r"^-?\d+$")
RE_DECIMAL = re.compile(r"^-?\d+\.\d+$")
RE_FRACCION = re.compile(r"^\d+/\d+$")
RE_ASIN = re.compile(r"^B[0-9A-Z]{9}$")
RE_ISBN10 = re.compile(r"^\d{9}[\dX]$")
RE_USERID = re.compile(r"^A[0-9A-Z]{5,20}$")
RE_HTML_ENTIDAD = re.compile(r"&(?:quot|amp|lt|gt|apos|#\d+);")
RE_HTML_TAG = re.compile(r"<\s*/?\s*[a-zA-Z][^>]*>")

MAX_EJEMPLOS = 5


# --------------------------------------------------------------------------- #
# Conteo de distintos / duplicados sin mantener todo en memoria
# --------------------------------------------------------------------------- #
class ContadorExterno:
    """Cuenta valores distintos y repeticiones usando hashes de 64 bits
    particionados en archivos temporales (una partición se procesa cada vez)."""

    def __init__(self, nombre, directorio, particiones=64, buffer_max=1_000_000):
        self.nombre = nombre
        self.particiones = particiones
        self.buffer_max = buffer_max
        self.rutas = [os.path.join(directorio, f"{nombre}_{i:03d}.bin") for i in range(particiones)]
        self.buffers = [array("q") for _ in range(particiones)]
        self.en_buffer = 0
        self.total = 0

    def agregar(self, clave):
        h = hash(clave)
        self.buffers[h % self.particiones].append(h)
        self.en_buffer += 1
        self.total += 1
        if self.en_buffer >= self.buffer_max:
            self._volcar()

    def _volcar(self):
        for ruta, buf in zip(self.rutas, self.buffers):
            if buf:
                with open(ruta, "ab") as f:
                    buf.tofile(f)
                del buf[:]
        self.en_buffer = 0

    def resultado(self):
        self._volcar()
        distintos = grupos_repetidos = max_repeticion = 0
        tamano_item = array("q").itemsize
        for ruta in self.rutas:
            if not os.path.exists(ruta):
                continue
            datos = array("q")
            with open(ruta, "rb") as f:
                datos.fromfile(f, os.path.getsize(ruta) // tamano_item)
            conteo = collections.Counter(datos)
            distintos += len(conteo)
            for c in conteo.values():
                if c > 1:
                    grupos_repetidos += 1
                    if c > max_repeticion:
                        max_repeticion = c
            os.remove(ruta)
        return {
            "total": self.total,
            "distintos": distintos,
            "registros_redundantes": self.total - distintos,
            "claves_repetidas": grupos_repetidos,
            "max_repeticiones_de_una_clave": max_repeticion,
        }


# --------------------------------------------------------------------------- #
# Estadísticas
# --------------------------------------------------------------------------- #
class Numerico:
    def __init__(self):
        self.n = 0
        self.suma = 0.0
        self.min = None
        self.max = None

    def agregar(self, x):
        self.n += 1
        self.suma += x
        if self.min is None or x < self.min:
            self.min = x
        if self.max is None or x > self.max:
            self.max = x

    def resumen(self):
        return {
            "n": self.n,
            "min": self.min,
            "max": self.max,
            "media": round(self.suma / self.n, 4) if self.n else None,
        }


def tipo_valor(valor):
    """Clasifica el formato de un valor crudo."""
    if valor == "":
        return "vacio"
    if valor.lower() == "unknown":
        return "unknown"
    if RE_ENTERO.match(valor):
        return "entero"
    if RE_DECIMAL.match(valor):
        return "decimal"
    if RE_FRACCION.match(valor):
        return "fraccion x/y"
    if " " not in valor and valor.isalnum():
        return "alfanumerico (sin espacios)"
    return "texto"


class Perfilador:
    def __init__(self, dir_temporal):
        self.registros = 0
        self.lineas = 0
        self.lineas_no_utf8 = 0
        self.lineas_continuacion = 0
        self.registros_sin_separador = 0

        self.apariciones = collections.Counter()
        self.registros_con_campo = collections.Counter()
        self.faltantes = collections.Counter()
        self.campo_repetido_en_registro = collections.Counter()
        self.vacios = collections.Counter()
        self.unknown = collections.Counter()
        self.espacios_extremos = collections.Counter()
        self.tipos = collections.defaultdict(collections.Counter)
        self.longitudes = collections.defaultdict(Numerico)
        self.campos_por_registro = collections.Counter()
        self.campos_inesperados = collections.Counter()
        self.ejemplos = collections.defaultdict(list)

        self.formato_product_id = collections.Counter()
        self.formato_user_id = collections.Counter()
        self.precio = Numerico()
        self.precio_invalido = 0
        self.score = collections.Counter()
        self.score_invalido = 0
        self.helpful = Numerico()
        self.helpful_total = Numerico()
        self.helpful_invalido = 0
        self.helpful_mayor_que_total = 0
        self.helpful_sin_votos = 0
        self.tiempo = Numerico()
        self.tiempo_invalido = 0
        self.por_anio = collections.Counter()
        self.por_mes = collections.Counter()
        self.cache_fecha = {}
        self.html_entidades = collections.Counter()
        self.html_tags = collections.Counter()

        d = dir_temporal
        self.distintos = {
            "productId": ContadorExterno("productId", d),
            "userId": ContadorExterno("userId", d),
            "registro_completo": ContadorExterno("registro_completo", d),
            "usuario_producto": ContadorExterno("usuario_producto", d),
            "usuario_producto_tiempo": ContadorExterno("usuario_producto_tiempo", d),
            "resena_sin_producto": ContadorExterno("resena_sin_producto", d),
            "producto_titulo": ContadorExterno("producto_titulo", d),
            "producto_precio": ContadorExterno("producto_precio", d),
        }

    def ejemplo(self, tipo, texto):
        lista = self.ejemplos[tipo]
        if len(lista) < MAX_EJEMPLOS:
            lista.append(texto[:200])

    # ----------------------------------------------------------------------- #
    def procesar_registro(self, campos, repetidos):
        """campos: dict clave -> valor (primera aparición)."""
        self.registros += 1
        self.campos_por_registro[len(campos)] += 1
        for c in repetidos:
            self.campo_repetido_en_registro[c] += 1

        for c in CAMPOS_ESPERADOS:
            if c in campos:
                self.registros_con_campo[c] += 1
            else:
                self.faltantes[c] += 1
                if self.faltantes[c] <= MAX_EJEMPLOS:
                    self.ejemplo(f"falta {c}", f"registro #{self.registros}")

        for c, v in campos.items():
            if v == "":
                self.vacios[c] += 1
            elif v.lower() == "unknown":
                self.unknown[c] += 1
            if v != v.strip():
                self.espacios_extremos[c] += 1
            self.tipos[c][tipo_valor(v)] += 1
            self.longitudes[c].agregar(len(v))

        pid = campos.get("product/productId", "")
        uid = campos.get("review/userId", "")
        self._validar_ids(pid, uid)
        self._validar_precio(campos.get("product/price"))
        self._validar_score(campos.get("review/score"))
        self._validar_helpfulness(campos.get("review/helpfulness"))
        self._validar_tiempo(campos.get("review/time"))
        for c in ("product/title", "review/summary", "review/text"):
            v = campos.get(c, "")
            if RE_HTML_ENTIDAD.search(v):
                self.html_entidades[c] += 1
            if RE_HTML_TAG.search(v):
                self.html_tags[c] += 1

        # Señales de duplicación (hash de las claves compuestas)
        sep = "\x1f"
        titulo = campos.get("product/title", "")
        precio = campos.get("product/price", "")
        t = campos.get("review/time", "")
        resumen = campos.get("review/summary", "")
        texto = campos.get("review/text", "")
        d = self.distintos
        d["productId"].agregar(pid)
        d["userId"].agregar(uid)
        d["registro_completo"].agregar(sep.join(campos.get(c, "") for c in CAMPOS_ESPERADOS))
        d["producto_titulo"].agregar(pid + sep + titulo)
        d["producto_precio"].agregar(pid + sep + precio)
        # Las claves basadas en usuario excluyen los userId "unknown" (anónimos)
        if uid and uid.lower() != "unknown":
            d["usuario_producto"].agregar(uid + sep + pid)
            d["usuario_producto_tiempo"].agregar(uid + sep + pid + sep + t)
            d["resena_sin_producto"].agregar(sep.join((uid, t, resumen, texto)))

    def _validar_ids(self, pid, uid):
        if RE_ASIN.match(pid):
            self.formato_product_id["ASIN (B + 9)"] += 1
        elif RE_ISBN10.match(pid):
            self.formato_product_id["ISBN-10"] += 1
        else:
            self.formato_product_id["otro"] += 1
            self.ejemplo("productId formato no estandar", pid)
        if uid.lower() == "unknown":
            self.formato_user_id["unknown"] += 1
        elif RE_USERID.match(uid):
            self.formato_user_id["A + alfanumerico"] += 1
        else:
            self.formato_user_id["otro"] += 1
            self.ejemplo("userId formato no estandar", uid)

    def _validar_precio(self, v):
        if v is None or v == "" or v.lower() == "unknown":
            return
        try:
            p = float(v)
        except ValueError:
            self.precio_invalido += 1
            self.ejemplo("precio no numerico", v)
            return
        if p < 0:
            self.ejemplo("precio negativo", v)
        self.precio.agregar(p)

    def _validar_score(self, v):
        if v is None:
            return
        try:
            s = float(v)
        except ValueError:
            self.score_invalido += 1
            self.ejemplo("score no numerico", v)
            return
        if not 1.0 <= s <= 5.0:
            self.score_invalido += 1
            self.ejemplo("score fuera de 1-5", v)
        self.score[v] += 1

    def _validar_helpfulness(self, v):
        if v is None:
            return
        if not RE_FRACCION.match(v):
            self.helpful_invalido += 1
            self.ejemplo("helpfulness con formato invalido", v)
            return
        a, b = (int(x) for x in v.split("/"))
        self.helpful.agregar(a)
        self.helpful_total.agregar(b)
        if b == 0:
            self.helpful_sin_votos += 1
        if a > b:
            self.helpful_mayor_que_total += 1
            self.ejemplo("helpfulness utiles > total", v)

    def _validar_tiempo(self, v):
        if v is None:
            return
        if not RE_ENTERO.match(v):
            self.tiempo_invalido += 1
            self.ejemplo("review/time no entero", v)
            return
        ts = int(v)
        fecha = self.cache_fecha.get(ts)
        if fecha is None:
            try:
                g = time.gmtime(ts)
                fecha = (g.tm_year, g.tm_mon)
            except (OverflowError, OSError, ValueError):
                fecha = False
            self.cache_fecha[ts] = fecha
        if not fecha:
            self.tiempo_invalido += 1
            self.ejemplo("review/time fuera de rango", v)
            return
        if ts % 86400 != 0:
            self.ejemplo("review/time con hora (no medianoche UTC)", v)
        self.tiempo.agregar(ts)
        self.por_anio[fecha[0]] += 1
        self.por_mes[f"{fecha[0]}-{fecha[1]:02d}"] += 1

    # ----------------------------------------------------------------------- #
    def procesar_archivo(self, ruta, limite=None, cada=1_000_000):
        inicio = time.time()
        campos, repetidos, ultima = {}, [], None

        def cerrar():
            nonlocal campos, repetidos, ultima
            if campos:
                self.procesar_registro(campos, repetidos)
            campos, repetidos, ultima = {}, [], None

        with gzip.open(ruta, "rb") as f:
            for raw in f:
                self.lineas += 1
                try:
                    linea = raw.decode("utf-8")
                except UnicodeDecodeError:
                    self.lineas_no_utf8 += 1
                    self.ejemplo("linea no UTF-8", repr(raw[:120]))
                    linea = raw.decode("latin-1")
                linea = linea.rstrip("\r\n")

                if linea == "":
                    cerrar()
                    if limite and self.registros >= limite:
                        break
                    if self.registros and self.registros % cada == 0:
                        seg = time.time() - inicio
                        print(f"  ... {self.registros:,} registros ({seg:,.0f} s, "
                              f"{self.registros / seg:,.0f} reg/s)", file=sys.stderr, flush=True)
                    continue

                m = RE_CLAVE.match(linea)
                if m is None:
                    # Línea sin "clave:" -> continuación del valor anterior (p. ej. saltos de línea en texto)
                    self.lineas_continuacion += 1
                    self.ejemplo("linea sin clave (continuacion)", linea)
                    if ultima is not None:
                        campos[ultima] += "\n" + linea
                    continue

                clave, valor = m.group(1), m.group(2) or ""
                self.apariciones[clave] += 1
                if clave not in CAMPOS_ESPERADOS:
                    self.campos_inesperados[clave] += 1
                    self.ejemplo(f"campo inesperado {clave}", linea)
                if clave == CAMPO_INICIO and campos:
                    # Empieza un registro nuevo sin línea vacía de separación
                    self.registros_sin_separador += 1
                    cerrar()
                if clave in campos:
                    repetidos.append(clave)
                else:
                    campos[clave] = valor
                ultima = clave
            else:
                cerrar()

        return time.time() - inicio

    # ----------------------------------------------------------------------- #
    def informe(self, archivo, segundos):
        n = self.registros or 1
        pct = lambda x: round(100 * x / n, 4)
        campos = CAMPOS_ESPERADOS + sorted(set(self.apariciones) - set(CAMPOS_ESPERADOS))

        por_campo = {}
        for c in campos:
            por_campo[c] = {
                "apariciones": self.apariciones[c],
                "registros_con_campo": self.registros_con_campo[c],
                "registros_sin_campo": self.faltantes[c],
                "pct_sin_campo": pct(self.faltantes[c]),
                "vacios": self.vacios[c],
                "pct_vacios": pct(self.vacios[c]),
                "unknown": self.unknown[c],
                "pct_unknown": pct(self.unknown[c]),
                "incompletos_total": self.faltantes[c] + self.vacios[c] + self.unknown[c],
                "con_espacios_extremos": self.espacios_extremos[c],
                "repetido_dentro_de_registro": self.campo_repetido_en_registro[c],
                "tipos": dict(self.tipos[c].most_common()),
                "longitud": self.longitudes[c].resumen(),
            }

        duplicados = {k: v.resultado() for k, v in self.distintos.items()}
        t = self.tiempo
        return {
            "archivo": archivo,
            "segundos": round(segundos, 1),
            "total_registros": self.registros,
            "total_lineas": self.lineas,
            "campos_encontrados": campos,
            "campos_por_registro": dict(sorted(self.campos_por_registro.items())),
            "campos_inesperados": dict(self.campos_inesperados),
            "por_campo": por_campo,
            "identificadores": {
                "formato_productId": dict(self.formato_product_id),
                "formato_userId": dict(self.formato_user_id),
                "productId_distintos": duplicados["productId"]["distintos"],
                "userId_distintos": duplicados["userId"]["distintos"],
            },
            "duplicados": duplicados,
            "rating": {
                "distribucion": dict(sorted(self.score.items())),
                "invalidos": self.score_invalido,
            },
            "precio": {**self.precio.resumen(), "no_numericos": self.precio_invalido},
            "helpfulness": {
                "utiles": self.helpful.resumen(),
                "total_votos": self.helpful_total.resumen(),
                "sin_votos (x/0)": self.helpful_sin_votos,
                "utiles_mayor_que_total": self.helpful_mayor_que_total,
                "formato_invalido": self.helpful_invalido,
            },
            "temporal": {
                "timestamp_min": t.min,
                "timestamp_max": t.max,
                "fecha_min": time.strftime("%Y-%m-%d", time.gmtime(t.min)) if t.min is not None else None,
                "fecha_max": time.strftime("%Y-%m-%d", time.gmtime(t.max)) if t.max is not None else None,
                "invalidos": self.tiempo_invalido,
                "por_anio": dict(sorted(self.por_anio.items())),
                "por_mes": dict(sorted(self.por_mes.items())),
            },
            "anomalias": {
                "lineas_no_utf8": self.lineas_no_utf8,
                "lineas_sin_clave_continuacion": self.lineas_continuacion,
                "registros_sin_linea_vacia_separadora": self.registros_sin_separador,
                "entidades_html": dict(self.html_entidades),
                "etiquetas_html": dict(self.html_tags),
                "ejemplos": dict(self.ejemplos),
            },
        }


# --------------------------------------------------------------------------- #
# Salida por consola
# --------------------------------------------------------------------------- #
def imprimir(inf):
    n = inf["total_registros"] or 1
    linea = "=" * 78

    def titulo(t):
        print(f"\n{linea}\n{t}\n{linea}")

    titulo("RESUMEN")
    print(f"Archivo:            {inf['archivo']}")
    print(f"Tiempo:             {inf['segundos']:,} s")
    print(f"Total registros:    {inf['total_registros']:,}")
    print(f"Total lineas:       {inf['total_lineas']:,}")
    print(f"Campos por registro: {inf['campos_por_registro']}")
    if inf["campos_inesperados"]:
        print(f"Campos inesperados: {inf['campos_inesperados']}")

    titulo("CAMPOS: APARICIONES, FALTANTES, VACIOS, UNKNOWN")
    print(f"{'campo':<22}{'apariciones':>14}{'faltantes':>12}{'vacios':>12}{'unknown':>14}{'% unknown':>11}")
    for c, d in inf["por_campo"].items():
        print(f"{c:<22}{d['apariciones']:>14,}{d['registros_sin_campo']:>12,}"
              f"{d['vacios']:>12,}{d['unknown']:>14,}{d['pct_unknown']:>10.2f}%")

    titulo("TIPOS / FORMATO DE VALORES Y LONGITUD")
    for c, d in inf["por_campo"].items():
        lon = d["longitud"]
        print(f"{c:<22} tipos={d['tipos']}")
        print(f"{'':<22} longitud min={lon['min']} max={lon['max']} media={lon['media']}")

    titulo("IDENTIFICADORES")
    ids = inf["identificadores"]
    print(f"productId distintos: {ids['productId_distintos']:,}  formatos={ids['formato_productId']}")
    print(f"userId distintos:    {ids['userId_distintos']:,}  formatos={ids['formato_userId']}")

    titulo("SEÑALES DE DUPLICACION")
    descripciones = {
        "registro_completo": "registro identico (10 campos)",
        "usuario_producto": "mismo userId + productId",
        "usuario_producto_tiempo": "mismo userId + productId + time",
        "resena_sin_producto": "misma resena (userId+time+summary+text) en otro producto",
        "producto_titulo": "pares productId+titulo (vs productId distintos)",
        "producto_precio": "pares productId+precio (vs productId distintos)",
    }
    dup = inf["duplicados"]
    for k, desc in descripciones.items():
        d = dup[k]
        print(f"{desc}")
        print(f"    total={d['total']:,} distintos={d['distintos']:,} redundantes={d['registros_redundantes']:,} "
              f"claves_repetidas={d['claves_repetidas']:,} max_rep={d['max_repeticiones_de_una_clave']:,}")
    print(f"productId con mas de un titulo: pares distintos {dup['producto_titulo']['distintos']:,} "
          f"vs productId distintos {ids['productId_distintos']:,}")
    print(f"productId con mas de un precio: pares distintos {dup['producto_precio']['distintos']:,} "
          f"vs productId distintos {ids['productId_distintos']:,}")

    titulo("DISTRIBUCION DE RATINGS (review/score)")
    for s, c in inf["rating"]["distribucion"].items():
        print(f"  {s:>5}: {c:>12,}  ({100 * c / n:6.2f}%)")
    print(f"  invalidos: {inf['rating']['invalidos']:,}")

    titulo("PRECIO Y HELPFULNESS")
    print(f"precio (solo numericos): {inf['precio']}")
    for k, v in inf["helpfulness"].items():
        print(f"helpfulness {k}: {v}")

    titulo("DISTRIBUCION TEMPORAL (review/time, año UTC)")
    tmp = inf["temporal"]
    print(f"Rango: {tmp['fecha_min']} -> {tmp['fecha_max']}   invalidos: {tmp['invalidos']:,}")
    for anio, c in tmp["por_anio"].items():
        print(f"  {anio}: {c:>12,}  ({100 * c / n:6.2f}%)")

    titulo("ANOMALIAS")
    a = inf["anomalias"]
    print(f"Lineas no UTF-8:                       {a['lineas_no_utf8']:,}")
    print(f"Lineas sin clave (continuacion):       {a['lineas_sin_clave_continuacion']:,}")
    print(f"Registros sin linea vacia separadora:  {a['registros_sin_linea_vacia_separadora']:,}")
    print(f"Registros con entidades HTML:          {a['entidades_html']}")
    print(f"Registros con etiquetas HTML:          {a['etiquetas_html']}")
    for c, d in inf["por_campo"].items():
        if d["con_espacios_extremos"] or d["repetido_dentro_de_registro"]:
            print(f"{c}: espacios al inicio/fin={d['con_espacios_extremos']:,} "
                  f"repetido en registro={d['repetido_dentro_de_registro']:,}")
    if a["ejemplos"]:
        print("\nEjemplos:")
        for tipo, lista in a["ejemplos"].items():
            print(f"  - {tipo}: {lista}")


def main():
    parser = argparse.ArgumentParser(description="Exploracion en streaming del dataset de resenas de Amazon (.txt.gz)")
    parser.add_argument("--archivo", required=True, help="Ruta al archivo .txt.gz")
    parser.add_argument("--limite", type=int, default=None, help="Procesar solo los primeros N registros (pruebas)")
    parser.add_argument("--salida", default=None, help="Ruta opcional para guardar el informe completo en JSON")
    parser.add_argument("--dir-temporal", default=None, help="Directorio para los hashes temporales (por defecto, el temporal del sistema)")
    args = parser.parse_args()

    if not os.path.isfile(args.archivo):
        sys.exit(f"No existe el archivo: {args.archivo}")

    print(f"Procesando {args.archivo} ({os.path.getsize(args.archivo):,} bytes comprimidos) en streaming...",
          file=sys.stderr)
    with tempfile.TemporaryDirectory(prefix="exploracion_", dir=args.dir_temporal) as tmp:
        perfil = Perfilador(tmp)
        segundos = perfil.procesar_archivo(args.archivo, limite=args.limite)
        informe = perfil.informe(args.archivo, segundos)

    imprimir(informe)
    if args.salida:
        os.makedirs(os.path.dirname(os.path.abspath(args.salida)), exist_ok=True)
        with open(args.salida, "w", encoding="utf-8") as f:
            json.dump(informe, f, ensure_ascii=False, indent=2)
        print(f"\nInforme JSON guardado en {args.salida}", file=sys.stderr)


if __name__ == "__main__":
    main()
