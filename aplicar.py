#!/usr/bin/env python3
"""MM_LFN - long file names for Multi Mente / nombres largos para Multi Mente.

  python aplicar.py MM.COM               ->  MM_LFN.COM, next to MM.COM / al lado de MM.COM
  python aplicar.py MM.COM -o OUT.COM

Hace falta el MM.COM ORIGINAL, sin tocar / You need the ORIGINAL, untouched MM.COM:
  2.07_A (23539 bytes, sha1 db7316e2b8f17deb1c34df909e2b8da8133e1601); 2.07A+ RC5 (23552 bytes, sha1 09c4a6b4f6fa4db19e94fa08fdcba0da2a3c29d0)
No hace falta nada mas que Python 3 / Nothing else is needed but Python 3.

Fichero generado por tools/hacer_parche.py: no lo edites a mano / generated file, do not edit.
"""
import base64
import hashlib
import locale
import os
import sys

# sha1 del original -> el parche (IPS) y lo que sale
BASES = {
  "db7316e2b8f17deb1c34df909e2b8da8133e1601": {
    "nombre": "2.07_A",
    "original": "db7316e2b8f17deb1c34df909e2b8da8133e1601",
    "tam_original": 23539,
    "parcheado": "479dade9e4d01e6477d9f07e29a0e7d5aa0e6911",
    "tam_parcheado": 25673,
    "ips": "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"
  },
  "09c4a6b4f6fa4db19e94fa08fdcba0da2a3c29d0": {
    "nombre": "2.07A+ RC5",
    "original": "09c4a6b4f6fa4db19e94fa08fdcba0da2a3c29d0",
    "tam_original": 23552,
    "parcheado": "5b97f818fc2496069c4aeef4e9cfcf2688dfe2bd",
    "tam_parcheado": 25673,
    "ips": "UEFUQ0gAAAEAAr9fADLAAAJS0AAzxAAC3z0AM9YAAo3QADRIAAKuXQA8BwAjKow+EQwAGTalI+shYckBBQDtsBE1ycOLPrfIRz4gzagVEPkAPGAAfLcgGHm3yP4gOBf+f9jWwDgQIZE9hW8wASR+yTwgA3k8yD4/yQEDBQcJDhASFBYYHB5BQUFBQUFBQ0VFRUVJSUlJRE5PT09PT3hPVVVVVVlUc2FhYWFhYWFjZWVlZWlpaWlkbm9vb29vL291dXV1eXR5RGF0ZTogLgAAAAAAPN0AAQAAPN8AIvWvMtk98cPENg4AeLfIfrfIzagVIwwQ9skRgAAOGsMFAAAAPUoAA83RywA9ggADw9nLAD2IAAPDBz0AV28ABc2SywAAAFwACEnd5eXVIgA+fv4uKEERDAAZfv6lIDgh+/w5fP7TOC8ixFwRAAIZIsZc7XPIXCrEXPnN3l31zfg9IVkgInET8dRUXe17yFzR4d3h0MO6E9Hh3eHDuhMqxlwGAH63KAUjBCD4BSrGXHj+DTALzeg9PgyRRw4At8k+ATLZPXj+IDALzeg9Ph+RzSA9GB/FBhTN6D0GAz4uzagVEPnBeNYIXxYAKsZcGQYIzeg9AQAAt8k62T23wNUhfSAicRM+A80gPTr6FfU+Bs1OFiHRPQYGzeg98c1OFtEhmCAicRPDwzUqAD4GC68PhiMQ+zLbPQ4ZzQUAMtw97VvEXA4azQUAIQAAIspcIuxcPv8y2j0qAD4RDQAZTiNGI34y7FwjXiNWKuxfOoNXtygOOuJfuCAKedYQKCyvGALtUiEBACgNerMgBzrsXD0y7FwbIyLMXO1T6lyvMt09zdde0DrdPT03yD7/Mto9IQAAOoNXtygY3SrEXBHXPQYQDkDNBQC3whtf3W4T3WYUfLUgHCrsXyLqXCEAACLsXCrmXwYEyzzLHRD6IsxcGDPrKsRcrw5+zQUAtyBqKsRcEQQAGRHqXAEEAO2wXiNWI34jy14oAxEAAO1TylxvJgAizFw63D0GAe1b6lwq7FwOc80FALcgMCHqXAYENCADIxD63SrEXAYQxc0dX8HIESAA3RkQ8yrMXCsizFx8tSDDKspcfLUgiTfJ3X4Atygo/uUoLN1+C/4PKCzd5eHtWwA+BgsaviAYIxMQ+CHdPcvGOto9tyABya83ySHdPcvOPv8y2j23yd1+DSHbPb4g8N1+AMt3KBPmHyjl/hUw4TLaPc2rXzYA3X4A5h8o0iHaPb4gxzV+zatf6yGEPQYNxeVOBgDd5eEJTiN+zWA9EhPhI8EQ6vYByW8mAE1EKQkpKQntS8ZcCckAAAAAKgYAEevTt+1SOA4hEGARkssBOQXtsMODVz7NMhtdIfJfBgZeI1YjxQEDAO2wwRDzw4NXSj4h/1+CPiqMPr8zzXYT1TTNAF1vWDb/OnJYT/IyNv99/jM4NCt+Nv8yqdDNJ8j1OqnQzSTIIQCirzY//iA4Bf5/MAF3LDwg8XchkT0RwKIBQADtsPHNJMg6T/LJrzKo0CH/X8kqjD42ABH/f82rzzgB6yLZ0Dqp0LfIIQAAOXz+wNh+/q7AI37+B8Ah/1/Nis/IItfQDhnNBQAy3D0hAAAizFwi7Fw6g1e3KDYh/19+/i4gDCN+/iAgBu1bGWAYHiHA/zn55d3hEdc9AUAQzQUA3V4T3VYUIUAAOfm3wHqzIBcq7F8i6lwq5l8GBMs8yx0Q+iLMXBEAAO1TylwRALAOGs0FACH/X+1bjD7Nq88wDBETABk2ABENABkY668yzNAR1c8OZM0FABG1zQ5jzQUAzSfIMsvQOqnQzSTIIQCgIsZcPv8y2j0hAKMi0NAi0tDtW8pcerMoQyHb0K8Ofs0FALfCmM06zNC3wpjNId/Q7VvQ0AEEAO2w7VPQ0F4jViN+Ms/QI8teKAMRAADtU8pcKtDQEQCwzavPOLUqzFx8tSAgKtLQ7VvQ0M2rzzBwEepcAQQA7bAi0tA6z9BvJgAizFx8tz4IIAS9OAF9R18WALftUiLMXMU63D3tW+pcKuxcDnPNBQDBtyA4OszQtyAyKupcWBYAGSLqXDAHKuxcIyLsXHiHh4eHR90hALDFzb/NwSgKESAA3RkQ8sMRzT4BGAGvMqjQOsvQzSTIEVEGDmTNBQARagUOY80FAMP4PfXFzZzNwfHDagXdfgC3yP7lKH3+Lih53X4L/g8oectfIG7d5eHNzM8yztAh2j1GNv8h2z2WsDLN0CrX0M2xzygTBgTFzYbPwSgHzbHPKAUQ8vYByd1+AP4FOs7QIAXlzczP4eVPEQGgGSkpKXzh5RESABl3Izal4eURASAZcSM2ADrN0LfMPM/hzYbPItfQyT7/Mto9t8ndfgDLdygg5h8o7v4VMOoy2j0y1NDdTg0h2z1xzatfNgAi1dDdfgDmHyjOIdo9viDI3X4NIds9viC/Ido9NSrV0BHz/xki1dDr3eXhLAaiTix+LLfEMs8KEhNOLH4st8QyzwoSE04sfiy3xDLPChITTix+LLfEMs8KEhNOLH4st8QyzwoSEywsLE4sfiy3xDLPChITTix+LLfEMs8KEhNOLH4st8QyzwoSE04sfiy3xDLPChITTix+LLfEMs8KEhNOLH4st8QyzwoSEywsTix+LLfEMs8KEhNOLH4st8QyzwoSE/YByTwgBHk8T8gOAcnlOtTQPc2rX363KAMjGPkRAGAZfLd9KAI+/9G3yE8GACEAoP4gMAjtsP4fyK8SyQ4U7bDrNi4jNi4jNi4j69YITyEAoAkOCO2wyREgABntW9nQzavPMBblEQsAGcteI37hIOf+pSDjfv4uKN7Jr8nlt+1S4cnlxd3l0Rr+BSACPuUGCxgDEyMaviACEPjB4ckGC68PhiMQ+8n1OszQPDLM0P4CMATxPgPJOsvQzSTI8c1RBvU6qdDNJMjxyTqo0NYB2BH/f82rzz/Y5RETABl+/qUrfuE3wPXNzM9P8W8mACkpKSkpEQCAGeshAAA5fP7A2M0nyEc6qdDNJMjrEarQxQEgAO2wwXjNJMg6qtC5N8A6q9C3yeXVzfjP0eHadhPKdhMhq9AGDM3oPT4MkQYgIAk6t9C3KAMGPq/FzSA9wTriVstnPlwgAXjNqBXxw9Az5dXN+M/R4doAXcq6E+XVIavQIsZczVRd0eHJAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABFT0Y="
  }
}

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
