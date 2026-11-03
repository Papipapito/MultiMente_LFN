# MM_LFN — nombres largos para Multi Mente (MSX)

Parcheador no oficial para **Multi Mente** (`MM.COM`, de MOGU). Hace que Multi Mente enseñe los **nombres largos**
(VFAT, los que se ven en Windows) en vez de `METALG~1.ROM` y, si tu `MM.COM` no lo lleva, le pone el **arreglo de
Nextor**. Vale para dos versiones: la **2.07_A** y la de la comunidad **2.07A+ RC5** (con arreglos de FAT16 y del año
2000). [English version](README.md).

```
antes:    ALESTE~1.ROM    FRAY2-~5.ROM    GOLVEL~5.ROM    KING'S~9.ROM    METALG~5.ROM
ahora:    Aleste 1 - E>   Fray 2 - Ver>   Golvellius 3>   King's Valle>   Metal Gear 3>
```

- **En la lista**, cada hueco enseña los 12 primeros caracteres del nombre largo (un `>` avisa de que sigue).
- **En File info**, el campo *Name:* enseña el nombre largo entero (hasta 31 caracteres).
- **En la vista de una columna** (`SHIFT+1`), la lista también enseña hasta 31 caracteres del nombre; para hacer
  sitio no pinta los indicadores de atributos (File info los sigue dando).
- Los ficheros sin nombre largo salen en 8.3, como siempre.

## Cómo aplicarlo

Hace falta tu propia copia del `MM.COM`. **No** va en este repositorio. Estas son las versiones que reconoce (la
versión de referencia de cada una):

| Versión | `MM.COM` | sha1 | Resultado |
| --- | --- | --- | --- |
| 2.07_A | 23.539 bytes | `db7316e2b8f17deb1c34df909e2b8da8133e1601` | 25.726 bytes, `e69bb4e32c1e86b301fc9e9053d8d264dec1ae0e` |
| 2.07A+ RC5 | 23.552 bytes | `09c4a6b4f6fa4db19e94fa08fdcba0da2a3c29d0` | 25.726 bytes, `12b9f581186abb647c90b37a0fef23ea55af0e83` |

La RC5 es la «MultiMente v2.07A+ RC5» de las descargas de MSX Resource Center. En su zip, el `MM.COM` en inglés es el
de la raíz del `MMv2.07Aplus-RC5.zip` interior (no el de `Japanese\`). Usa el `MM.EXE` que viene con tu `MM.COM`; el
parcheador no lo toca.

El parcheador pone solo lo que falta:

- **Los nombres largos**, siempre.
- **El arreglo de Nextor**, si tu `MM.COM` no lo lleva. Es el cambio de un byte que describe la
  [wiki de MSX.org](https://msx.org/wiki/MultiMente) (`3A E1 5F CB 4F CA` → `C3`; evita el «Not MSX-DOS Disk» con
  Nextor). Las dos versiones de referencia de arriba ya lo llevan, y el parche de nombres largos lo necesita:
  reutiliza código que ese arreglo deja sin uso.
- **Lo que hayas cambiado con CS** (la tabla de programas por extensión, etc.) se conserva: la versión se reconoce
  sin mirar esa zona y el parche no escribe nada dentro.
- Cualquier otro `MM.COM` al que le falte el arreglo de Nextor recibe **solo el arreglo**, guardado como
  `MM_NEXTOR.COM` (el arreglo es el de la wiki; no lo hemos probado en esas versiones). Todo lo demás se rechaza.

Elige una de estas:

1. **Página web, sin instalar nada:** abre [el aplicador en línea](https://papipapito.github.io/MultiMente_LFN/aplicar.html)
   (o el [`aplicar.html`](aplicar.html) descargado) en el navegador y suelta encima tu `MM.COM`. Todo ocurre en tu
   navegador: el fichero no se sube a ningún sitio.
2. **Python 3:** `python aplicar.py MM.COM` → escribe `MM_LFN.COM` al lado.
3. **Cualquier parcheador de IPS** (Floating IPS, Lunar IPS…): aplica [`MM_LFN.ips`](MM_LFN.ips) (2.07_A) o
   [`MM_LFN_RC5.ips`](MM_LFN_RC5.ips) (RC5) a `MM.COM`. Los parcheadores de IPS no comprueban el fichero de origen y
   el `.ips` no pone el arreglo de Nextor: comprueba antes que tu fichero es una de las dos versiones de arriba
   (el sha1, o al menos el tamaño) y que lleva el arreglo; si no, usa la página web o `aplicar.py`.

Después copia el resultado a la tarjeta como `MM.COM`, en la carpeta de Multi Mente (junto a `MM.EXE` y `MM.CFG`).
`aplicar.py` y `aplicar.html` comprueban el resultado antes de dártelo.

## Requisitos y límites

- **Nextor 2.1 o 3.0**, FAT16 o FAT12 (Nextor no lee FAT32). Con otro DOS, o si algo falla, se ven los 8.3.
- **Solo para ver.** Copiar, mover, renombrar y borrar siguen igual, con el 8.3; lo que MM copia o crea no lleva
  nombre largo. Ordenar ordena por el 8.3.
- Solo ASCII: las letras latinas acentuadas salen sin acento y lo demás como `?`.
- Necesita un segmento libre del mapper (un mapper de 256 KB o más) y sitio en la cima del TPA (≥ `D411h`;
  Nextor 2.1.4 deja `D806h` y Nextor 3.0 `D706h`). Si falta uno de los dos, la lista se queda en 8.3 y solo File
  info enseña el nombre largo.
- Entrar en una carpeta tarda algo más (unos 0,9 s con 200 ficheros de nombre largo en openMSX); mover el cursor
  no lee el disco.
- Siguen los límites propios de Multi Mente: el manual de la 2.07A+ RC5 dice que no se use Sort ni el Filer en FAT16
  y que «wr[Y]ting» se ignora allí.
- Probado solo en openMSX (Philips NMS 8245, 4 MB, Sunrise IDE, imagen FAT16): la 2.07_A con Nextor 2.1.1, 2.1.4 y
  3.0.0 beta 2; la RC5 con Nextor 2.1.1 y 2.1.4 (con Nextor 3.0 todavía no). En las dos: lista, File info, ordenar,
  marcar, entrar en carpetas, volver de programas de `[X]ecom`, borrar, copiar y `CS MM` (el fichero parcheado pesa
  unos 2,1 KB más, y CS solo toca el bloque de configuración). En hardware real no se ha probado. El detalle, con la
  lista de lo que se probó, está en [docs/TECNICO.md](docs/TECNICO.md).

## Reconstruirlo y probarlo

El parche es Z80 escrito a mano (`src/mmlfn.asm`) sobre el desensamblado del binario. Con
[pasmo](http://pasmo.speccy.org/) (o WSL en Windows) y los originales en `original/` (`MM.COM` para la 2.07_A,
`MM_RC5.COM` para la RC5):

```
python tools/hacer_parche.py     # construye los .ips, aplicar.py y aplicar.html
python tests/probar.py           # prueba las tres formas de aplicarlo (node es opcional)
```

`tests/openmsx/probar_mm.py` ejecuta un `MM.COM` parcheado dentro de openMSX (Nextor en un Sunrise IDE, una imagen FAT16
con ficheros de nombre largo) y saca capturas de la lista y de File info; las opciones están en su cabecera. Necesita
openMSX, las ROM del sistema y tus propios ficheros de MSX-DOS 2, que no van en este repositorio.

## Sobre Multi Mente y este parche

Multi Mente es obra de MOGU. Este repositorio es un complemento no oficial y no cuenta con el aval del autor.
**No contiene nada del código de Multi Mente**: los `.ips` llevan solo los bytes nuevos (unos 2,5 KB cada uno) y las
herramientas comprueban que cada byte del parche es distinto del original en su sitio. Hay que traer el propio
`MM.COM`. Si el autor o quien tenga los derechos se opone, que lo diga y se retira.

El código de este repositorio (la fuente del parche y las herramientas) va bajo la GNU GPL v3, ver
[LICENSE](LICENSE).
