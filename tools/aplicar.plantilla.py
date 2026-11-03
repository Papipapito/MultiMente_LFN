#!/usr/bin/env python3
"""MM_LFN - long file names for Multi Mente / nombres largos para Multi Mente.

  python aplicar.py MM.COM               ->  MM_LFN.COM, next to MM.COM / al lado de MM.COM
  python aplicar.py MM.COM -o OUT.COM

Hace falta el MM.COM ORIGINAL, sin tocar / You need the ORIGINAL, untouched MM.COM:
  __LISTA__
No hace falta nada mas que Python 3 / Nothing else is needed but Python 3.

Fichero generado por tools/hacer_parche.py: no lo edites a mano / generated file, do not edit.
"""
import base64
import hashlib
import locale
import os
import sys

# sha1 del original -> el parche (IPS) y lo que sale
BASES = __BASES__

try:
    locale.setlocale(locale.LC_ALL, "")
except locale.Error:
    pass
ES = (os.environ.get("MMLFN_LANG") or locale.getlocale()[0] or os.environ.get("LANG", "")).lower().startswith(("es", "spanish"))


def T(es, en):
    return es if ES else en


def aplicar_ips(datos, ips):
    if ips[:5] != b"PATCH":
        raise ValueError("not an IPS patch")
    out = bytearray(datos)
    i = 5
    while ips[i:i + 3] != b"EOF":
        off = int.from_bytes(ips[i:i + 3], "big")
        n = int.from_bytes(ips[i + 3:i + 5], "big")
        i += 5
        if n:
            dato = ips[i:i + n]
            i += n
        else:  # registro RLE / RLE record
            n = int.from_bytes(ips[i:i + 2], "big")
            dato = ips[i + 2:i + 3] * n
            i += 3
        if off > len(out):
            out.extend(bytes(off - len(out)))
        out[off:off + n] = dato
    return bytes(out)


def main(argv):
    salida = None
    if "-o" in argv:
        k = argv.index("-o")
        if k + 1 >= len(argv):
            sys.exit(__doc__)
        salida = argv[k + 1]
        del argv[k:k + 2]
    if len(argv) != 1 or argv[0] in ("-h", "--help"):
        sys.exit(__doc__)
    entrada = argv[0]
    try:
        datos = open(entrada, "rb").read()
    except OSError as e:
        sys.exit(T("No puedo leer %s: %s", "Cannot read %s: %s") % (entrada, e))
    sha = hashlib.sha1(datos).hexdigest()
    if any(sha == b["parcheado"] for b in BASES.values()):
        sys.exit(T("%s ya lleva el parche de nombres largos.", "%s already has the long-name patch.") % entrada)
    if sha not in BASES:
        sys.exit(T(
            "%s no es un MM.COM original que conozca.\n  sha1 de tu fichero: %s\n  Valen:\n    %s\n"
            "El parche solo vale para esas versiones exactas, sin tocar (no sirve un MM.COM ya parcheado "
            "o con las asociaciones cambiadas).",
            "%s is not an original MM.COM I know.\n  your file's sha1: %s\n  These fit:\n    %s\n"
            "The patch only fits those exact versions, untouched (a MM.COM that is already patched "
            "or has edited associations will not do).") % (entrada, sha, "\n    ".join(
                "%s: %s" % (b["nombre"], s) for s, b in BASES.items())))
    base = BASES[sha]
    nuevo = aplicar_ips(datos, base64.b64decode(base["ips"]))
    if hashlib.sha1(nuevo).hexdigest() != base["parcheado"]:
        sys.exit(T("Error interno: el resultado no es el esperado.", "Internal error: unexpected result."))
    if salida is None:
        salida = os.path.join(os.path.dirname(os.path.abspath(entrada)), "MM_LFN.COM")
    if os.path.abspath(salida) == os.path.abspath(entrada):
        sys.exit(T("No sobrescribo el original: usa otro nombre con -o.", "Not overwriting the original: use another name with -o."))
    with open(salida, "wb") as f:
        f.write(nuevo)
    print(T("Multi Mente %s: hecho. %s (%d bytes, sha1 %s)", "Multi Mente %s: done. %s (%d bytes, sha1 %s)")
          % (base["nombre"], salida, len(nuevo), base["parcheado"]))
    print(T("Copialo a la tarjeta como MM.COM, en la carpeta de Multi Mente (junto a MM.EXE y MM.CFG).",
            "Copy it to the card as MM.COM, in the Multi Mente folder (next to MM.EXE and MM.CFG)."))


if __name__ == "__main__":
    main(sys.argv[1:])
