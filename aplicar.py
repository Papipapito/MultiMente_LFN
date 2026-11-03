#!/usr/bin/env python3
"""MM_LFN - long file names for Multi Mente 2.07_A / nombres largos para Multi Mente 2.07_A.

  python aplicar.py MM.COM               ->  MM_LFN.COM, next to MM.COM / al lado de MM.COM
  python aplicar.py MM.COM -o OUT.COM

Hace falta el MM.COM ORIGINAL de Multi Mente 2.07_A (23539 bytes, sha1 db7316e2b8f17deb1c34df909e2b8da8133e1601).
You need the ORIGINAL MM.COM of Multi Mente 2.07_A (23539 bytes, sha1 db7316e2b8f17deb1c34df909e2b8da8133e1601).
No hace falta nada mas que Python 3 / Nothing else is needed but Python 3.

Fichero generado por tools/hacer_parche.py: no lo edites a mano / generated file, do not edit.
"""
import base64
import hashlib
import locale
import os
import sys

SHA1_ORIGINAL = "db7316e2b8f17deb1c34df909e2b8da8133e1601"
SHA1_PARCHEADO = "479dade9e4d01e6477d9f07e29a0e7d5aa0e6911"
IPS = base64.b64decode(
    "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"
)

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
    if sha == SHA1_PARCHEADO:
        sys.exit(T("%s ya lleva el parche de nombres largos.", "%s already has the long-name patch.") % entrada)
    if sha != SHA1_ORIGINAL:
        sys.exit(T(
            "%s no es el MM.COM original de Multi Mente 2.07_A.\n  sha1 de tu fichero: %s\n  sha1 esperado:      %s\n"
            "El parche solo vale para esa version exacta (y sin tocar: no sirve un MM.COM ya parcheado "
            "o con las asociaciones cambiadas).",
            "%s is not the original Multi Mente 2.07_A MM.COM.\n  your file's sha1: %s\n  expected sha1:    %s\n"
            "The patch only fits that exact version, untouched (a MM.COM that is already patched "
            "or has edited associations will not do).") % (entrada, sha, SHA1_ORIGINAL))
    nuevo = aplicar_ips(datos, IPS)
    if hashlib.sha1(nuevo).hexdigest() != SHA1_PARCHEADO:
        sys.exit(T("Error interno: el resultado no es el esperado.", "Internal error: unexpected result."))
    if salida is None:
        salida = os.path.join(os.path.dirname(os.path.abspath(entrada)), "MM_LFN.COM")
    if os.path.abspath(salida) == os.path.abspath(entrada):
        sys.exit(T("No sobrescribo el original: usa otro nombre con -o.", "Not overwriting the original: use another name with -o."))
    with open(salida, "wb") as f:
        f.write(nuevo)
    print(T("Hecho: %s (%d bytes, sha1 %s)", "Done: %s (%d bytes, sha1 %s)") % (salida, len(nuevo), SHA1_PARCHEADO))
    print(T("Copialo a la tarjeta como MM.COM, en la carpeta de Multi Mente (junto a MM.EXE y MM.CFG).",
            "Copy it to the card as MM.COM, in the Multi Mente folder (next to MM.EXE and MM.CFG)."))


if __name__ == "__main__":
    main(sys.argv[1:])
