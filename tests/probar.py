"""probar.py — pruebas de los aplicadores (aplicar.py, aplicar.html y MM_LFN.ips).

Uso:  python tests/probar.py [original/MM.COM]

Necesita el MM.COM original (no va en el repo). Para el aplicador de la pagina web, node.
No necesita pasmo: prueba lo que se reparte, no la compilacion (eso lo hace tools/hacer_parche.py).
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHA1_ORIGINAL = "db7316e2b8f17deb1c34df909e2b8da8133e1601"
SHA1_PARCHEADO = "479dade9e4d01e6477d9f07e29a0e7d5aa0e6911"
fallos = []


def comprueba(nombre, cond, detalle=""):
    print(("  ok    " if cond else "  FALLA ") + nombre + ("" if cond else "  " + str(detalle)))
    if not cond:
        fallos.append(nombre)


def aplicar(*args, cwd=None):
    return subprocess.run([sys.executable, os.path.join(RAIZ, "aplicar.py"), *args], capture_output=True, text=True,
                          cwd=cwd, env={**os.environ, "MMLFN_LANG": "en", "PYTHONIOENCODING": "utf-8"})


def main():
    ruta = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, "original", "MM.COM")
    if not os.path.exists(ruta):
        sys.exit("Falta el MM.COM original (%s); no va en el repo." % ruta)
    orig = open(ruta, "rb").read()
    assert hashlib.sha1(orig).hexdigest() == SHA1_ORIGINAL, "%s no es el MM.COM 2.07_A original" % ruta

    with tempfile.TemporaryDirectory() as tmp:
        print("aplicar.py")
        entrada = os.path.join(tmp, "MM.COM")
        open(entrada, "wb").write(orig)
        r = aplicar(entrada)
        salida = os.path.join(tmp, "MM_LFN.COM")
        comprueba("original -> MM_LFN.COM al lado, codigo 0", r.returncode == 0 and os.path.exists(salida), r.stderr)
        nuevo = open(salida, "rb").read() if os.path.exists(salida) else b""
        comprueba("sha1 del resultado", hashlib.sha1(nuevo).hexdigest() == SHA1_PARCHEADO)
        comprueba("el original no se toca", open(entrada, "rb").read() == orig)

        r = aplicar(salida, "-o", os.path.join(tmp, "otro.com"))
        comprueba("un MM.COM ya parcheado se rechaza", r.returncode != 0 and "already" in r.stderr and
                  not os.path.exists(os.path.join(tmp, "otro.com")), r.stderr)

        malo = bytearray(orig)
        malo[0x500] ^= 1
        open(os.path.join(tmp, "malo.com"), "wb").write(malo)
        r = aplicar(os.path.join(tmp, "malo.com"), "-o", os.path.join(tmp, "malo_out.com"))
        comprueba("un byte distinto se rechaza y no escribe nada",
                  r.returncode != 0 and "sha1" in r.stderr and not os.path.exists(os.path.join(tmp, "malo_out.com")), r.stderr)

        open(os.path.join(tmp, "corto.com"), "wb").write(orig[:1000])
        r = aplicar(os.path.join(tmp, "corto.com"))
        comprueba("un fichero truncado se rechaza", r.returncode != 0, r.stderr)

        r = aplicar(entrada, "-o", entrada)
        comprueba("no sobrescribe el original", r.returncode != 0 and open(entrada, "rb").read() == orig, r.stderr)

        r = aplicar(os.path.join(tmp, "no_existe.com"))
        comprueba("fichero inexistente", r.returncode != 0 and "Cannot read" in r.stderr, r.stderr)

        r = aplicar("-o", os.path.join(tmp, "x.com"), entrada)
        comprueba("-o antes del fichero", r.returncode == 0 and os.path.exists(os.path.join(tmp, "x.com")), r.stderr)

        r = aplicar()
        comprueba("sin argumentos: ayuda", r.returncode != 0 and "python aplicar.py" in r.stderr)

        print("MM_LFN.ips (aplicador IPS independiente, el del script)")
        sys.path.insert(0, RAIZ)
        import importlib
        mod = importlib.import_module("aplicar")
        ips = open(os.path.join(RAIZ, "MM_LFN.ips"), "rb").read()
        comprueba("el IPS es el que lleva aplicar.py", ips == mod.IPS)
        comprueba("IPS sobre el original da el sha1 esperado",
                  hashlib.sha1(mod.aplicar_ips(orig, ips)).hexdigest() == SHA1_PARCHEADO)
        comprueba("el IPS pesa mucho menos que el programa (solo bytes nuevos)", len(ips) < len(orig) // 5, len(ips))

        print("aplicar.html (nucleo en node)")
        node = shutil.which("node")
        if not node:
            print("  (sin node: se salta)")
        else:
            html = open(os.path.join(RAIZ, "aplicar.html"), encoding="utf-8").read()
            js = re.search(r"<script>(.*?)</script>", html, re.S).group(1)
            prueba = os.path.join(tmp, "nucleo.js")
            open(prueba, "w", encoding="utf-8").write(js + r"""
;(function () {
  const fs = require("fs"), crypto = require("crypto");
  const sal = [];
  const ok = (n, c) => sal.push((c ? "  ok    " : "  FALLA ") + n);
  const hex = b => crypto.createHash("sha1").update(b).digest("hex");
  for (const n of [0, 1, 54, 55, 56, 57, 63, 64, 65, 119, 120, 1000, 23539, 100003]) {
    const b = crypto.randomBytes(n);
    ok("sha1 de " + n + " bytes", sha1(new Uint8Array(b)) === hex(b));
  }
  const orig = new Uint8Array(fs.readFileSync(process.argv[2]));
  const nuevo = aplicarIps(orig, ipsBytes());
  ok("IPS sobre el original: sha1 y tamano", sha1(nuevo) === SHA1_PARCHEADO && nuevo.length === __LEN__);
  ok("comprobar(original)", comprobar(orig) === "original");
  ok("comprobar(parcheado)", comprobar(nuevo) === "parcheado");
  const malo = orig.slice(); malo[0x500] ^= 1;
  ok("comprobar(un byte distinto)", comprobar(malo) === "otro");
  ok("comprobar(vacio)", comprobar(new Uint8Array(0)) === "otro");
  const py = new Uint8Array(fs.readFileSync(process.argv[3]));
  ok("identico byte a byte al de aplicar.py", Buffer.compare(Buffer.from(nuevo), Buffer.from(py)) === 0);
  console.log(sal.join("\n")); process.exit(sal.some(s => s.includes("FALLA")) ? 1 : 0);
})();
""".replace("__LEN__", str(len(nuevo))))
            r = subprocess.run([node, prueba, ruta, salida], capture_output=True, text=True)
            print(r.stdout.rstrip())
            if r.returncode:
                fallos.append("node")
                print(r.stderr)

    print("\n%s" % ("TODO BIEN" if not fallos else "FALLAN: " + ", ".join(fallos)))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
