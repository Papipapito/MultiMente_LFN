#!/usr/bin/env python3
"""MM_LFN - Multi Mente patcher: long file names + Nextor fix / parcheador de Multi Mente: nombres largos + arreglo de Nextor.

  python aplicar.py MM.COM               ->  MM_LFN.COM, next to MM.COM / al lado de MM.COM
  python aplicar.py MM.COM -o OUT.COM

Sirve para estas versiones / It fits these versions (as they come, or with their CS settings changed, with or
without the Nextor fix / tal cual, o con los ajustes cambiados con CS, con o sin el arreglo de Nextor):
  __LISTA__
Pone solo lo que falte / It adds only what is missing:
  - el arreglo de Nextor (3A E1 5F CB 4F CA -> C3, wiki de MSX.org) si no lo lleva / the Nextor fix, if it is not there;
  - los nombres largos / the long file names.
Lo que hayas cambiado con CS se conserva / What you changed with CS is kept.
No hace falta nada mas que Python 3 / Nothing else is needed but Python 3.

Fichero generado por tools/hacer_parche.py: no lo edites a mano / generated file, do not edit.
"""
import base64
import hashlib
import locale
import os
import re
import sys

# sha1 (sin la zona de configuracion) del MM.COM de referencia, con el arreglo de Nextor -> el parche (IPS) y lo que sale
BASES = __BASES__
# zona de configuracion (lo que cambia CS): se pone a cero para reconocer la version
CFG_LO, CFG_HI = __CFG_LO__, __CFG_HI__
# el sitio del arreglo de Nextor: 3A E1 5F CB 4F CA -> C3
ARREGLO = re.compile(rb"\x3a\xe1\x5f\xcb\x4f([\xca\xc3])\x4a\x3e")

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


def sha1(datos):
    return hashlib.sha1(datos).hexdigest()


def sha1_cfg(datos):
    m = bytearray(datos)
    m[CFG_LO:CFG_HI] = bytes(len(m[CFG_LO:CFG_HI]))
    return sha1(m)


def version_de(datos):
    m = re.search(rb"MM v2\.\d\d[A-Za-z_+]{0,3}", datos)
    return m.group(0).decode("ascii") if m else None


def analizar(datos):
    """estado: 'original' (se le pueden poner los nombres largos), 'parcheado' (ya los lleva) u 'otro'.
    arreglo: 'ya' (lleva el arreglo de Nextor), 'falta' o None (no se encuentra el sitio, o esta mas de una vez)."""
    sitios = [m.start() + 5 for m in ARREGLO.finditer(datos)]
    pos = sitios[0] if len(sitios) == 1 else None
    arreglo = None if pos is None else ("ya" if datos[pos] == 0xC3 else "falta")
    arreglado = bytearray(datos)
    if arreglo == "falta":
        arreglado[pos] = 0xC3
    arreglado = bytes(arreglado)
    h = sha1_cfg(arreglado)
    base = BASES.get(h)
    estado = "original" if base else "otro"
    if not base:
        base = next((b for b in BASES.values() if b["parcheado_cfg"] == h), None)
        estado = "parcheado" if base else "otro"
    return dict(estado=estado, base=base, arreglo=arreglo, arreglado=arreglado)


def procesar(datos):
    """Devuelve dict(salida, nombre, hechos, base, estado, arreglo, version).
    salida: los bytes nuevos, o None si no hay nada que hacer o no se puede. hechos: 'nextor' y/o 'lfn'.
    nombre: MM_LFN.COM (lleva los nombres largos) o MM_NEXTOR.COM (solo el arreglo de Nextor)."""
    a = analizar(datos)
    r = dict(salida=None, nombre="MM_LFN.COM", hechos=[], base=a["base"], estado=a["estado"], arreglo=a["arreglo"],
             version=version_de(datos))
    if a["estado"] == "original":
        base = a["base"]
        salida = aplicar_ips(a["arreglado"], base64.b64decode(base["ips"]))
        if sha1_cfg(salida) != base["parcheado_cfg"] or len(salida) != base["tam_parcheado"] or (
                sha1(datos) == base["original"] and sha1(salida) != base["parcheado"]):
            raise RuntimeError(T("Error interno: el resultado no es el esperado.", "Internal error: unexpected result."))
        r.update(salida=salida, hechos=(["nextor"] if a["arreglo"] == "falta" else []) + ["lfn"])
    elif a["arreglo"] == "falta":  # ya con nombres largos o version desconocida: solo el arreglo de Nextor
        r.update(salida=a["arreglado"], hechos=["nextor"], nombre="MM_LFN.COM" if a["estado"] == "parcheado" else "MM_NEXTOR.COM")
    return r


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
    r = procesar(datos)
    versiones = "\n    ".join("%s: %d bytes, sha1 %s" % (b["nombre"], b["tam_original"], b["original"]) for b in BASES.values())
    if r["salida"] is None:
        if r["estado"] == "parcheado":
            sys.exit(T("%s ya lleva el parche de nombres largos (y el arreglo de Nextor).",
                       "%s already has the long-name patch (and the Nextor fix).") % entrada)
        sys.exit(T(
            "%s no es un MM.COM que conozca.\n  version que dice ser: %s\n  sha1 de tu fichero: %s\n  Valen (tal cual o con los ajustes de CS "
            "cambiados, con o sin el arreglo de Nextor):\n    %s\n"
            "No sirve un MM.COM de otra version ni con el codigo cambiado.",
            "%s is not an MM.COM I know.\n  version it claims to be: %s\n  your file's sha1: %s\n  These fit (as they come, or with the CS settings "
            "changed, with or without the Nextor fix):\n    %s\n"
            "A MM.COM of another version, or with changed code, will not do.") % (
                entrada, r["version"] or "?", sha1(datos), versiones))
    if salida is None:
        salida = os.path.join(os.path.dirname(os.path.abspath(entrada)), r["nombre"])
    if os.path.abspath(salida) == os.path.abspath(entrada):
        sys.exit(T("No sobrescribo el original: usa otro nombre con -o.", "Not overwriting the original: use another name with -o."))
    with open(salida, "wb") as f:
        f.write(r["salida"])
    nombre = r["base"]["nombre"] if r["base"] else (r["version"] or "?")
    hechos = {"nextor": T("arreglo de Nextor", "Nextor fix"), "lfn": T("nombres largos", "long file names")}
    print(T("Multi Mente %s: hecho. Puesto: %s. %s (%d bytes)", "Multi Mente %s: done. Added: %s. %s (%d bytes)")
          % (nombre, T(" y ", " and ").join(hechos[h] for h in r["hechos"]), salida, len(r["salida"])))
    if r["arreglo"] == "ya" and "lfn" in r["hechos"]:
        print(T("Ya llevaba el arreglo de Nextor. Lo que hayas cambiado con CS se conserva.",
                "It already had the Nextor fix. What you changed with CS is kept."))
    if "lfn" not in r["hechos"]:
        print(T("Esta version no la conozco para los nombres largos: solo he puesto el arreglo de Nextor (el de la wiki de MSX.org, "
                "sin probar en esta version).",
                "I do not know this version for long file names: I only added the Nextor fix (the one on the MSX.org wiki, "
                "untested on this version)."))
    print(T("Copialo a la tarjeta como MM.COM, en la carpeta de Multi Mente (junto a MM.EXE y MM.CFG).",
            "Copy it to the card as MM.COM, in the Multi Mente folder (next to MM.EXE and MM.CFG)."))


if __name__ == "__main__":
    main(sys.argv[1:])
