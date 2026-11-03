"""hacer_parche.py — de MM.COM original a todo lo que se reparte.

Uso:  python tools/hacer_parche.py [original/MM.COM]

1. Comprueba que el original es Multi Mente 2.07_A (sha1).
2. Lo parchea con src/parchear.py (ensambla src/mmlfn.asm con pasmo).
3. Saca de la diferencia el parche IPS: SOLO los bytes nuevos, ni un byte del original.
4. Lo reaplica sobre el original y comprueba que sale el mismo fichero.
5. Escribe MM_LFN.ips, aplicar.py y aplicar.html (con el parche dentro).

Necesita pasmo (http://pasmo.speccy.org/): en el PATH o, en Windows, dentro de WSL.
"""
import base64
import hashlib
import os
import re
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHA1_ORIGINAL = "db7316e2b8f17deb1c34df909e2b8da8133e1601"
VERSION = "2.07_A"


def sha1(b):
    return hashlib.sha1(b).hexdigest()


def hacer_ips(orig, nuevo):
    """IPS con solo los bytes que cambian (y todo lo que se anade al final)."""
    assert len(nuevo) >= len(orig)
    trozos = []
    i = 0
    while i < len(nuevo):
        if i < len(orig) and orig[i] == nuevo[i]:
            i += 1
            continue
        j = i
        while j < len(nuevo) and (j >= len(orig) or orig[j] != nuevo[j]) and j - i < 0xFFFF:
            j += 1
        trozos.append((i, nuevo[i:j]))
        i = j
    out = bytearray(b"PATCH")
    for off, datos in trozos:
        assert off != 0x454F46, "el desplazamiento coincide con la marca EOF del IPS"
        out += off.to_bytes(3, "big") + len(datos).to_bytes(2, "big") + datos
    out += b"EOF"
    return bytes(out), trozos


def aplicar_ips(datos, ips):
    """Aplicador de IPS (el mismo algoritmo que aplicar.py, para comprobar)."""
    assert ips[:5] == b"PATCH"
    out = bytearray(datos)
    i = 5
    while ips[i:i + 3] != b"EOF":
        off = int.from_bytes(ips[i:i + 3], "big")
        n = int.from_bytes(ips[i + 3:i + 5], "big")
        i += 5
        assert n, "RLE no soportado"
        out[off:off + n] = ips[i:i + n]
        i += n
    return bytes(out)


def plantilla(nombre, **datos):
    texto = open(os.path.join(RAIZ, "tools", nombre), encoding="utf-8").read()
    for k, v in datos.items():
        texto = texto.replace("__%s__" % k, v)
    sobran = re.findall(r"__[A-Z0-9_]+__", texto)
    assert not sobran, "%s: marcas sin rellenar %s" % (nombre, sobran)
    return texto


def main():
    ruta = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, "original", "MM.COM")
    orig = open(ruta, "rb").read()
    if sha1(orig) != SHA1_ORIGINAL:
        sys.exit("%s no es el MM.COM %s original (sha1 %s)" % (ruta, VERSION, SHA1_ORIGINAL))
    with tempfile.TemporaryDirectory() as tmp:
        nuevo_ruta = os.path.join(tmp, "MM_LFN.COM")
        subprocess.run([sys.executable, os.path.join(RAIZ, "src", "parchear.py"), ruta, nuevo_ruta], check=True)
        nuevo = open(nuevo_ruta, "rb").read()
    ips, trozos = hacer_ips(orig, nuevo)
    assert aplicar_ips(orig, ips) == nuevo, "el IPS no reproduce el MM.COM parcheado"
    # nada del original dentro del parche: cada byte del IPS cae en un hueco nuevo o cambia
    for off, datos in trozos:
        for k, b in enumerate(datos):
            assert off + k >= len(orig) or orig[off + k] != b
    sha_nuevo = sha1(nuevo)
    b64 = base64.b64encode(ips).decode()
    datos = dict(IPS_B64=b64, SHA1_ORIGINAL=SHA1_ORIGINAL, SHA1_PARCHEADO=sha_nuevo, VERSION=VERSION,
                 TAM_ORIGINAL=str(len(orig)), TAM_PARCHEADO=str(len(nuevo)))
    open(os.path.join(RAIZ, "MM_LFN.ips"), "wb").write(ips)
    for plant, destino in (("aplicar.plantilla.py", "aplicar.py"), ("aplicar.plantilla.html", "aplicar.html")):
        with open(os.path.join(RAIZ, destino), "w", encoding="utf-8", newline="\n") as f:
            f.write(plantilla(plant, **datos))
    print("MM_LFN.ips: %d bytes en %d trozos (%d bytes nuevos o cambiados de %d)"
          % (len(ips), len(trozos), sum(len(d) for _, d in trozos), len(nuevo)))
    print("original  %d bytes sha1 %s" % (len(orig), SHA1_ORIGINAL))
    print("parcheado %d bytes sha1 %s" % (len(nuevo), sha_nuevo))


if __name__ == "__main__":
    main()
