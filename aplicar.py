#!/usr/bin/env python3
"""MM_LFN - Multi Mente patcher: long file names + Nextor fix / parcheador de Multi Mente: nombres largos + arreglo de Nextor.

  python aplicar.py MM.COM               ->  MM_LFN.COM, next to MM.COM / al lado de MM.COM
  python aplicar.py MM.COM -o OUT.COM

Sirve para estas versiones / It fits these versions (as they come, or with their CS settings changed, with or
without the Nextor fix / tal cual, o con los ajustes cambiados con CS, con o sin el arreglo de Nextor):
  2.07_A (23539 bytes, sha1 db7316e2b8f17deb1c34df909e2b8da8133e1601); 2.07A+ RC5 (23552 bytes, sha1 09c4a6b4f6fa4db19e94fa08fdcba0da2a3c29d0)
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
BASES = {
  "4f17e6cd6ecaf32dcd87b65303699842d6a3aed1": {
    "nombre": "2.07_A",
    "original": "db7316e2b8f17deb1c34df909e2b8da8133e1601",
    "original_cfg": "4f17e6cd6ecaf32dcd87b65303699842d6a3aed1",
    "tam_original": 23539,
    "parcheado": "e69bb4e32c1e86b301fc9e9053d8d264dec1ae0e",
    "parcheado_cfg": "7f4e119fcd7c8b5f8e0a2ed37cccabdf6a848d6a",
    "tam_parcheado": 25726,
    "ips": "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"
  },
  "d4ebb297d4d2d67fe341e812145a118b36e2ec7b": {
    "nombre": "2.07A+ RC5",
    "original": "09c4a6b4f6fa4db19e94fa08fdcba0da2a3c29d0",
    "original_cfg": "d4ebb297d4d2d67fe341e812145a118b36e2ec7b",
    "tam_original": 23552,
    "parcheado": "12b9f581186abb647c90b37a0fef23ea55af0e83",
    "parcheado_cfg": "af64b3e92aeebea1a319431bc3bc0119a114e92f",
    "tam_parcheado": 25726,
    "ips": "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"
  }
}
# zona de configuracion (lo que cambia CS): se pone a cero para reconocer la version
CFG_LO, CFG_HI = 238, 872
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
