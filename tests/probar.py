"""probar.py — pruebas de los aplicadores (aplicar.py, aplicar.html y los .ips).

Uso:  python tests/probar.py

Necesita los MM.COM originales en original/ (no van en el repo): MM.COM (2.07_A) y/o MM_RC5.COM (2.07A+ RC5);
se prueba cada uno que este. Para el aplicador de la pagina web, node.
No necesita pasmo: prueba lo que se reparte, no la compilacion (eso lo hace tools/hacer_parche.py).
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
    ("2.07_A", "MM.COM", "db7316e2b8f17deb1c34df909e2b8da8133e1601", "479dade9e4d01e6477d9f07e29a0e7d5aa0e6911", "MM_LFN.ips"),
    ("2.07A+ RC5", "MM_RC5.COM", "09c4a6b4f6fa4db19e94fa08fdcba0da2a3c29d0", "5b97f818fc2496069c4aeef4e9cfcf2688dfe2bd",
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


def prueba_base(nombre, orig, sha_orig, sha_nuevo, ips_nombre, tmp, node):
    print("== Multi Mente %s" % nombre)
    d = os.path.join(tmp, re.sub(r"\W", "_", nombre))
    os.makedirs(d)
    p = lambda f: os.path.join(d, f)
    entrada, salida = p("MM.COM"), p("MM_LFN.COM")
    open(entrada, "wb").write(orig)

    print("aplicar.py")
    r = aplicar(entrada)
    comprueba("original -> MM_LFN.COM al lado, codigo 0", r.returncode == 0 and os.path.exists(salida), r.stderr)
    nuevo = open(salida, "rb").read() if os.path.exists(salida) else b""
    comprueba("sha1 del resultado", sha1(nuevo) == sha_nuevo)
    comprueba("el original no se toca", open(entrada, "rb").read() == orig)
    comprueba("dice la version", nombre in r.stdout, r.stdout)

    r = aplicar(salida, "-o", p("otro.com"))
    comprueba("un MM.COM ya parcheado se rechaza", r.returncode != 0 and "already" in r.stderr and
              not os.path.exists(p("otro.com")), r.stderr)

    malo = bytearray(orig)
    malo[0x500] ^= 1
    open(p("malo.com"), "wb").write(malo)
    r = aplicar(p("malo.com"), "-o", p("malo_out.com"))
    comprueba("un byte distinto se rechaza y no escribe nada",
              r.returncode != 0 and "sha1" in r.stderr and not os.path.exists(p("malo_out.com")), r.stderr)

    open(p("corto.com"), "wb").write(orig[:1000])
    r = aplicar(p("corto.com"))
    comprueba("un fichero truncado se rechaza", r.returncode != 0, r.stderr)

    r = aplicar(entrada, "-o", entrada)
    comprueba("no sobrescribe el original", r.returncode != 0 and open(entrada, "rb").read() == orig, r.stderr)

    r = aplicar("-o", p("x.com"), entrada)
    comprueba("-o antes del fichero", r.returncode == 0 and os.path.exists(p("x.com")), r.stderr)

    print("%s (IPS)" % ips_nombre)
    sys.path.insert(0, RAIZ)
    mod = importlib.import_module("aplicar")
    ips = open(os.path.join(RAIZ, ips_nombre), "rb").read()
    comprueba("el IPS es el que lleva aplicar.py", base64.b64decode(mod.BASES[sha_orig]["ips"]) == ips)
    comprueba("IPS sobre el original da el sha1 esperado", sha1(mod.aplicar_ips(orig, ips)) == sha_nuevo)
    comprueba("el IPS pesa mucho menos que el programa (solo bytes nuevos)", len(ips) < len(orig) // 5, len(ips))

    print("aplicar.html (nucleo en node)")
    if not node:
        print("  (sin node: se salta)")
        return
    html = open(os.path.join(RAIZ, "aplicar.html"), encoding="utf-8").read()
    js = re.search(r"<script>(.*?)</script>", html, re.S).group(1)
    prueba = p("nucleo.js")
    open(prueba, "w", encoding="utf-8").write(js + r"""
;(function () {
  const fs = require("fs"), crypto = require("crypto");
  const sal = [];
  const ok = (n, c) => sal.push((c ? "  ok    " : "  FALLA ") + n);
  const hex = b => crypto.createHash("sha1").update(b).digest("hex");
  for (const n of [0, 1, 55, 56, 63, 64, 65, 119, 120, 1000, 23539, 100003]) {
    const b = crypto.randomBytes(n);
    ok("sha1 de " + n + " bytes", sha1(new Uint8Array(b)) === hex(b));
  }
  const orig = new Uint8Array(fs.readFileSync(process.argv[2]));
  const sha = sha1(orig);
  const nuevo = aplicarIps(orig, ipsBytes(sha));
  ok("IPS sobre el original: sha1 y tamano", sha1(nuevo) === BASES[sha].parcheado && nuevo.length === BASES[sha].tam_parcheado);
  ok("comprobar(original)", comprobar(orig).estado === "original");
  ok("comprobar(parcheado)", comprobar(nuevo).estado === "parcheado" && comprobar(nuevo).base.original === sha);
  const malo = orig.slice(); malo[0x500] ^= 1;
  ok("comprobar(un byte distinto)", comprobar(malo).estado === "otro");
  ok("comprobar(vacio)", comprobar(new Uint8Array(0)).estado === "otro");
  const py = new Uint8Array(fs.readFileSync(process.argv[3]));
  ok("identico byte a byte al de aplicar.py", Buffer.compare(Buffer.from(nuevo), Buffer.from(py)) === 0);
  console.log(sal.join("\n")); process.exit(sal.some(s => s.includes("FALLA")) ? 1 : 0);
})();
""")
    r = subprocess.run([node, prueba, entrada, salida], capture_output=True, text=True)
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
            assert sha1(orig) == sha_orig, "%s no es el MM.COM %s original" % (ruta, nombre)
            prueba_base(nombre, orig, sha_orig, sha_nuevo, ips_nombre, tmp, node)
            hechas += 1
        if not hechas:
            sys.exit("Faltan los MM.COM originales en original/ (no van en el repo).")
        print("== comunes")
        r = aplicar(os.path.join(tmp, "no_existe.com"))
        comprueba("fichero inexistente", r.returncode != 0 and "Cannot read" in r.stderr, r.stderr)
        r = aplicar()
        comprueba("sin argumentos: ayuda", r.returncode != 0 and "python aplicar.py" in r.stderr)
        open(os.path.join(tmp, "basura.com"), "wb").write(os.urandom(5000))
        r = aplicar(os.path.join(tmp, "basura.com"))
        comprueba("un fichero cualquiera se rechaza y lista las versiones", r.returncode != 0 and "RC5" in r.stderr, r.stderr)

    print("\n%s" % ("TODO BIEN" if not fallos else "FALLAN: " + ", ".join(fallos)))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
