"""probar.py — pruebas de los aplicadores (aplicar.py, aplicar.html y los .ips).

Uso:  python tests/probar.py

Necesita los MM.COM de referencia en original/ (no van en el repo): MM.COM (2.07_A) y/o MM_RC5.COM (2.07A+ RC5);
se prueba cada uno que este. Para el aplicador de la pagina web, node.
No necesita pasmo: prueba lo que se reparte, no la compilacion (eso lo hace tools/hacer_parche.py).

Por cada version se prueba, con aplicar.py y con el nucleo de aplicar.html (mismos ficheros, mismos resultados):
  A  el original tal cual                      -> nombres largos
  B  el original sin el arreglo de Nextor      -> arreglo de Nextor + nombres largos (el mismo fichero que A)
  C  con la tabla de programas cambiada (CS)   -> nombres largos, la tabla se conserva
  D  C sin el arreglo de Nextor                -> igual que C
  E  ya parcheado                              -> rechazado ("ya lleva el parche")
  F  ya parcheado pero sin el arreglo          -> solo el arreglo de Nextor
  G  version desconocida sin el arreglo        -> solo el arreglo de Nextor (MM_NEXTOR.COM)
  H  version desconocida con el arreglo        -> rechazado
  y ficheros truncados, basura, sin el sitio del arreglo...
"""
import base64
import hashlib
import importlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# nombre, fichero original, sha1 del original, sha1 del parcheado, fichero IPS
BASES = [
    ("2.07_A", "MM.COM", "db7316e2b8f17deb1c34df909e2b8da8133e1601", "e69bb4e32c1e86b301fc9e9053d8d264dec1ae0e", "MM_LFN.ips"),
    ("2.07A+ RC5", "MM_RC5.COM", "09c4a6b4f6fa4db19e94fa08fdcba0da2a3c29d0", "12b9f581186abb647c90b37a0fef23ea55af0e83",
     "MM_LFN_RC5.ips"),
]
fallos = []


def sha1(b):
    return hashlib.sha1(b).hexdigest()


def comprueba(nombre, cond, detalle=""):
    print(("  ok    " if cond else "  FALLA ") + nombre + ("" if cond else "  " + str(detalle)))
    if not cond:
        fallos.append(nombre)


def aplicar(*args):
    return subprocess.run([sys.executable, os.path.join(RAIZ, "aplicar.py"), *args], capture_output=True, text=True,
                          env={**os.environ, "MMLFN_LANG": "en", "PYTHONIOENCODING": "utf-8"})


def sin_arreglo(datos, pos):
    m = bytearray(datos)
    assert m[pos] == 0xC3
    m[pos] = 0xCA
    return bytes(m)


def escenarios(orig, parcheado, mod):
    """{id: (entrada, salida esperada o None, nombre del fichero de salida esperado)}, hechos a mano."""
    pos = [m.start() + 5 for m in re.finditer(rb"\x3a\xe1\x5f\xcb\x4f\xc3\x4a\x3e", orig)]
    assert len(pos) == 1, "el original de referencia debe llevar el arreglo de Nextor, una vez"
    pos = pos[0]
    lo, hi = mod.CFG_LO, mod.CFG_HI

    def con_cfg(datos):  # lo que haria CS: otra tabla de programas
        m = bytearray(datos)
        m[0x200:0x20C] = b"CAMBIADO CS!"
        m[0x328:0x330] = b"OPFXSD $"
        assert m[lo:hi] != datos[lo:hi]
        return bytes(m)

    parcheado_cfg = con_cfg(parcheado)
    desconocida = bytearray(orig)
    desconocida[0x500] ^= 1  # codigo distinto, fuera de la zona de configuracion
    desconocida = bytes(desconocida)
    return {
        "A": (orig, parcheado, "MM_LFN.COM"),
        "B": (sin_arreglo(orig, pos), parcheado, "MM_LFN.COM"),
        "C": (con_cfg(orig), parcheado_cfg, "MM_LFN.COM"),
        "D": (sin_arreglo(con_cfg(orig), pos), parcheado_cfg, "MM_LFN.COM"),
        "E": (parcheado, None, None),
        "F": (sin_arreglo(parcheado, pos), parcheado, "MM_LFN.COM"),
        "G": (sin_arreglo(desconocida, pos), desconocida, "MM_NEXTOR.COM"),
        "H": (desconocida, None, None),
        "I_corto": (orig[:1000], None, None),
        "J_basura": (bytes(range(256)) * 40, None, None),
        "K_sin_sitio": (orig[:pos] + b"\x00" + orig[pos + 1:], None, None),
        "L_vacio": (b"", None, None),
    }, pos


def prueba_base(nombre, orig, sha_orig, sha_nuevo, ips_nombre, tmp, node):
    print("== Multi Mente %s" % nombre)
    d = os.path.join(tmp, re.sub(r"\W", "_", nombre))
    os.makedirs(d)
    p = lambda *f: os.path.join(d, *f)
    sys.path.insert(0, RAIZ)
    mod = importlib.import_module("aplicar")
    ips = open(os.path.join(RAIZ, ips_nombre), "rb").read()
    parcheado = mod.aplicar_ips(orig, ips)

    print("%s (IPS)" % ips_nombre)
    comprueba("IPS sobre el original da el sha1 esperado", sha1(parcheado) == sha_nuevo)
    base = [b for b in mod.BASES.values() if b["original"] == sha_orig][0]
    comprueba("el IPS es el que lleva aplicar.py", base64.b64decode(base["ips"]) == ips)
    comprueba("el IPS pesa mucho menos que el programa (solo bytes nuevos)", len(ips) < len(orig) // 5, len(ips))
    comprueba("el sha1 sin la zona de configuracion es el de aplicar.py",
              mod.sha1_cfg(orig) in mod.BASES and mod.sha1_cfg(parcheado) == base["parcheado_cfg"])

    esc, pos = escenarios(orig, parcheado, mod)
    print("aplicar.py")
    for k, (entrada, esperado, nombre_sal) in esc.items():
        sub = p("py_" + k)
        os.makedirs(sub)
        ruta = os.path.join(sub, "MM.COM")
        open(ruta, "wb").write(entrada)
        r = aplicar(ruta)
        salidas = sorted(f for f in os.listdir(sub) if f != "MM.COM")
        if esperado is None:
            comprueba("%s: rechazado, codigo != 0 y no escribe nada" % k, r.returncode != 0 and not salidas, r.stdout + r.stderr)
        else:
            sal = open(os.path.join(sub, nombre_sal), "rb").read() if nombre_sal in salidas else None
            comprueba("%s: codigo 0, escribe %s y es lo esperado" % (k, nombre_sal), r.returncode == 0 and sal == esperado,
                      (r.returncode, salidas, r.stderr))
        comprueba("%s: el original no se toca" % k, open(ruta, "rb").read() == entrada)
        if k == "A":
            comprueba("A: sha1 del resultado", sha1(sal or b"") == sha_nuevo)
            comprueba("A: dice la version y lo que puso", nombre in r.stdout and "Added: long file names" in r.stdout, r.stdout)
        if k == "B":
            comprueba("B: dice que puso el arreglo de Nextor", "Added: Nextor fix and long file names" in r.stdout, r.stdout)
        if k == "C":
            comprueba("C: la tabla cambiada con CS se conserva y nada mas dentro de la zona",
                      sal is not None and sal[mod.CFG_LO:mod.CFG_HI] == entrada[mod.CFG_LO:mod.CFG_HI])
        if k == "E":
            comprueba("E: dice que ya esta parcheado", "already" in r.stderr, r.stderr)
        if k == "G":
            comprueba("G: avisa de que no conoce la version", "do not know this version" in r.stdout, r.stdout)
        if k in ("H", "J_basura"):
            comprueba("%s: lista las versiones que valen" % k, "RC5" in r.stderr and "2.07_A" in r.stderr, r.stderr)

    entrada = p("py_A", "MM.COM")
    r = aplicar(entrada, "-o", entrada)
    comprueba("no sobrescribe el original", r.returncode != 0 and open(entrada, "rb").read() == orig, r.stderr)
    r = aplicar("-o", p("x.com"), entrada)
    comprueba("-o antes del fichero", r.returncode == 0 and open(p("x.com"), "rb").read() == parcheado, r.stderr)

    print("aplicar.html (nucleo en node)")
    if not node:
        print("  (sin node: se salta)")
        return
    nd = p("nodo")
    os.makedirs(nd)
    for k, (entrada, esperado, nombre_sal) in esc.items():
        open(os.path.join(nd, k + ".in"), "wb").write(entrada)
        if esperado is not None:
            open(os.path.join(nd, k + ".out"), "wb").write(esperado)
            open(os.path.join(nd, k + ".nombre"), "w").write(nombre_sal)
    html = open(os.path.join(RAIZ, "aplicar.html"), encoding="utf-8").read()
    js = re.search(r"<script>(.*?)</script>", html, re.S).group(1)
    prueba = p("nucleo.js")
    open(prueba, "w", encoding="utf-8").write(js + r"""
;(function () {
  const fs = require("fs"), crypto = require("crypto"), path = require("path");
  const dir = process.argv[2], sal = [];
  const ok = (n, c) => sal.push((c ? "  ok    " : "  FALLA ") + n);
  const hex = b => crypto.createHash("sha1").update(b).digest("hex");
  for (const n of [0, 1, 55, 56, 63, 64, 65, 119, 120, 1000, 23539, 100003]) {
    const b = crypto.randomBytes(n);
    ok("sha1 de " + n + " bytes", sha1(new Uint8Array(b)) === hex(b));
  }
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith(".in")).sort()) {
    const k = f.slice(0, -3), entrada = new Uint8Array(fs.readFileSync(path.join(dir, f)));
    const r = procesar(entrada), fout = path.join(dir, k + ".out");
    if (fs.existsSync(fout)) {
      const esperado = fs.readFileSync(fout), nombre = fs.readFileSync(path.join(dir, k + ".nombre"), "utf8");
      ok(k + ": mismos bytes y nombre que aplicar.py", r.salida !== null && Buffer.compare(Buffer.from(r.salida), esperado) === 0 && r.nombre === nombre);
    } else {
      ok(k + ": rechazado (sin salida)", r.salida === null);
    }
  }
  const A = new Uint8Array(fs.readFileSync(path.join(dir, "A.in")));
  ok("estado de A / E / H", procesar(A).estado === "original" &&
     procesar(new Uint8Array(fs.readFileSync(path.join(dir, "E.in")))).estado === "parcheado" &&
     procesar(new Uint8Array(fs.readFileSync(path.join(dir, "H.in")))).estado === "otro");
  ok("version de A", /^MM v2\.07/.test(versionDe(A) || ""));
  console.log(sal.join("\n")); process.exit(sal.some(s => s.includes("FALLA")) ? 1 : 0);
})();
""")
    r = subprocess.run([node, prueba, nd], capture_output=True, text=True)
    print(r.stdout.rstrip())
    if r.returncode:
        fallos.append("node " + nombre)
        print(r.stderr)


def main():
    hechas = 0
    node = shutil.which("node")
    with tempfile.TemporaryDirectory() as tmp:
        for nombre, fichero, sha_orig, sha_nuevo, ips_nombre in BASES:
            ruta = os.path.join(RAIZ, "original", fichero)
            if not os.path.exists(ruta):
                print("== Multi Mente %s: falta original/%s, se salta" % (nombre, fichero))
                continue
            orig = open(ruta, "rb").read()
            assert sha1(orig) == sha_orig, "%s no es el MM.COM %s de referencia" % (ruta, nombre)
            prueba_base(nombre, orig, sha_orig, sha_nuevo, ips_nombre, tmp, node)
            hechas += 1
        if not hechas:
            sys.exit("Faltan los MM.COM de referencia en original/ (no van en el repo).")
        print("== comunes")
        r = aplicar(os.path.join(tmp, "no_existe.com"))
        comprueba("fichero inexistente", r.returncode != 0 and "Cannot read" in r.stderr, r.stderr)
        r = aplicar()
        comprueba("sin argumentos: ayuda", r.returncode != 0 and "python aplicar.py" in r.stderr)

    print("\n%s" % ("TODO BIEN" if not fallos else "FALLAN: " + ", ".join(fallos)))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
