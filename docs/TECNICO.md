# Multi Mente con nombres largos — notas técnicas

Documento de referencia del parche (versión 2): qué hace, límites, cómo funciona por dentro y qué se
probó. Para aplicarlo, ver el [LEEME](../LEEME.md).

Multi Mente 2.07_A (MOGU) solo se publicó en binario: el parche está hecho a mano sobre el
desensamblado. `src/mmlfn.asm` es el código nuevo y `src/parchear.py` lo ensambla con
[pasmo](http://pasmo.speccy.org/) y lo aplica al MM.COM original; `tools/hacer_parche.py` hace de ahí
el `MM_LFN.ips` y los aplicadores.

Vale para dos bases (`src/parchear.py` elige por el sha1; ver «La variante RC5» más abajo):

| Base | Original | Parcheado |
| --- | --- | --- |
| 2.07_A | 23.539 bytes, sha1 `db7316e2b8f17deb1c34df909e2b8da8133e1601` | 25.673 bytes, sha1 `479dade9e4d01e6477d9f07e29a0e7d5aa0e6911` |
| 2.07A+ RC5 | 23.552 bytes, sha1 `09c4a6b4f6fa4db19e94fa08fdcba0da2a3c29d0` | 25.673 bytes, sha1 `5b97f818fc2496069c4aeef4e9cfcf2688dfe2bd` |

Todo lo que sigue (direcciones, zonas, pruebas) se escribió y se midió sobre la 2.07_A; la RC5 tiene el mismo código
en las mismas direcciones, y lo que cambia se cuenta al final.

## Cómo se ve

```
antes:    ALESTE~1.ROM    FRAY2-~5.ROM    GOLVEL~5.ROM    KING'S~9.ROM    METALG~5.ROM
ahora:    Aleste 1 - E>   Fray 2 - Ver>   Golvellius 3>   King's Valle>   Metal Gear 3>
```

- En la lista, en todas las vistas (1, 2, 3 y 5 columnas; en las de 1-3, el tamaño y la
  fecha siguen en su sitio). Los que no tienen nombre largo salen en 8.3, como siempre.
- En File info, si el nombre cabe en el campo (12 caracteres), se pinta en su sitio. Si es
  más largo, ocupa toda la fila hasta el recuadro de `Wild:` (31 caracteres) y tapa la
  fecha de ese fichero; `Size:` y `Time:` siguen en la fila de abajo. Si pasa de 31: los
  20 primeros, `...` y los 8 últimos (para que se vea la extensión):
  `Nombre_muy_largo_de_...s_xx.dsk`.

## Limitaciones

- **Solo para ver.** Copiar, mover, renombrar y borrar siguen igual: Multi Mente trabaja con
  el 8.3 y lo que copia o crea no lleva nombre largo. Si se renombra un fichero, sus
  entradas LFN viejas se quedan en el disco; el parche comprueba el checksum y no las enseña
  (sale el 8.3 nuevo).
- **Lo que se ve en la lista es el principio del nombre.** La extensión casi nunca llega a
  verse, y en las colecciones muchos nombres comparten los 12 primeros caracteres (lo que
  cambia es el final: `(JP)`, `[a]`...); File info enseña el nombre entero. El color por
  extensión sigue saliendo del 8.3, y **ordenar ordena por el 8.3** (los `~1`, `~2` no
  siguen el orden de los nombres largos). Sin ordenar se ve el orden del directorio: el
  alfabético de los nombres largos en las tarjetas de MSX SD Maker; en una copia hecha desde
  Windows, el orden en que se copió.
- **Caracteres:** ASCII. Las letras latinas acentuadas salen sin acento (`Música española ñ`
  → `Musica espanola n`), porque la fuente de MM es la de la BIOS (japonesa en muchas
  máquinas). Lo demás (japonés, símbolos) sale como `?`. Lo que busca por nombre sigue
  usando el 8.3.
- **Necesita Nextor 2.1 o 3.0** (usa `_RDDRV`, `_GETCLUS` y lo que guarda el FIB de
  Nextor). Con otro DOS, o si algo falla, se ve el 8.3. Solo FAT16 y FAT12: Nextor no lee
  FAT32.
- **Necesita un segmento del mapper** para la tabla de nombres: se queda el último de los
  que MM reserva para copiar (hasta 64). Si MM consigue menos de dos (un mapper de 128 KB),
  se le deja el suyo y la lista sigue en 8.3; File info lee entonces el nombre del disco en
  cada movimiento del cursor, como en la versión 1.
- **Y sitio en la página 3:** el código va en `CB92h-D0EAh` (MM usa hasta `CB91h` y deja el
  resto para la pila). Si la cima del TPA está por debajo de `D3EBh`, el parche se queda
  como en la versión 1: nombre largo solo en File info. Con Nextor 2.1.4 la cima es `D806h`
  y con Nextor 3.0 `D706h` (NMS 8245 en openMSX).
- **Más de 256 ficheros:** MM se queda como mucho con 257 entradas y la tabla tiene sitio
  para 256: la última sale en 8.3.
- **Algo más lento al entrar en una carpeta:** cada vez que MM la lista (al entrar, al
  volver de un programa, después de copiar o borrar...) se lee entero su directorio. En
  openMSX (Sunrise IDE, Nextor 2.1.4), una carpeta de 200 ficheros con nombres de 32 a 53
  caracteres (912 entradas) tarda **0,86 s más** (listar 3,2 s y pintar 1,6 s: +18 %): 0,25 s
  leyendo de 8 en 8 sectores, 0,1 s de interrupciones y el resto juntando y convirtiendo los
  9.230 caracteres; con Nextor 3.0, 0,9 s. Una de 17 ficheros, 0,1 s más; la raíz, 0,05 s.
  A cambio, mover el cursor no lee el disco.
- Cada `_RDDRV` hace que Nextor vacíe e invalide sus búferes de esa unidad (es como está
  hecho Nextor); no se pierde nada, solo que el siguiente acceso al disco los vuelve a leer.
- Si el disco da un error mientras se leen los nombres, se ignora y la lista sigue en 8.3
  (el error de verdad ya lo habría dado MM al listar). Si Nextor lo reintenta y se repite,
  sale el diálogo de MM; con Abort se deja todo como estaba y sigue lo de MM, como si el
  error hubiera salido al listar. Sin tabla, File info lee el disco
  como en la versión 1: si el medio falla, el diálogo de error de MM puede salir al mover el
  cursor. Con Abort se vuelve bien; con Retry, el nombre puede salir con el color del
  diálogo hasta el siguiente movimiento.

## Cómo funciona

Al listar un directorio, MM guarda cada entrada en un registro de 32 bytes con el mismo
formato que una entrada FAT (`5FFFh + 32·n`, en el orden del directorio), y no usa los
bytes 12-21 (comprobado con puntos de vigilancia en openMSX al listar, ordenar, marcar,
árbol, copiar y borrar).

1. **Al arrancar** (`0100h`): el código de la página 3 va en MM.COM detrás de lo de la
   versión 1. Al cargar cae en `5FBFh+`, donde MM pone luego sus marcas y sus registros; el
   arranque lo copia a `CB92h` antes de saltar a MM. Si no cabe, deja como en la versión 1
   los sitios que llaman a la página 3.
2. **El segmento** (`586Fh`): cuando MM acaba la lista de segmentos que se queda para copiar
   (`C831h`, acabada en `FFh`), se le quita el último. Pedirlo antes no vale: MM hace
   `_FORK` al empezar (`5783h`) y lo pedido antes de eso no se libera con el `_JOIN` de la
   vuelta de un programa (se perdía un segmento en cada vuelta). Ahí mismo se hace en el
   segmento la tabla para convertir los caracteres.
3. **Al listar:** `3E4Ah` marca la tabla como no válida; `3E88h` (de la versión 1) guarda en
   cada registro la marca `A5h` y la posición de la entrada que da el FIB de Nextor.
4. **Al acabar el listado** (`3E82h`), la pasada por el directorio, con el segmento en la
   página 2. Solo en el listado de siempre (el que se llama desde `07ABh`, al entrar en una
   carpeta y al volver a ella): ahí se sabe qué rutina de abort tiene puesta MM. Los otros
   (como `1AFFh`) vuelven a listar luego por `07ABh`. La pasada saca primero con
   `_GETCLUS` la cadena de clusters (tras cada `_RDDRV` Nextor vuelve a leer la FAT: así se
   lee una vez) y lee el directorio con `_RDDRV` de 8 en 8 sectores, sin pasar de un
   cluster. El primer cluster de una carpeta es el del registro de
   `.`; si el patrón del listado lo ha dejado fuera, el de `_FFIRST "."`; la raíz, con el
   `_DPARM` que hace MM. Junta las entradas LFN de cada 8.3 (comprobando orden y checksum) y
   la casa por el nombre con el registro que toca, porque los dos van en el mismo orden; si
   no es ese, mira los 4 siguientes (los que se salta se quedan sin nombre largo). Para cada
   registro, la tabla guarda el checksum de su 8.3 y el nombre ya como se pinta (hasta 31
   caracteres).
5. **La entrada de la tabla va en el propio registro** (byte 18, y la marca `A5h` en el 19):
   MM mueve los registros enteros al ordenar (las carpetas primero), y al borrar no vuelve
   a listar; la entrada se mueve con el registro.
6. **Al pintar** un elemento de la lista (`33BFh`, la llamada a `1376h`) y en File info
   (`34D5h`) se copia la entrada del segmento (se pone en la página 2 solo para eso). Si el
   checksum no es el del 8.3 del registro (cambiado sin volver a listar), la lista pinta el
   8.3 y File info lee el disco como en la versión 1: ese sector y el anterior, juntando las
   entradas LFN que preceden a la 8.3, o recorriendo el directorio.

Durante la pasada hay una rutina propia de errores de disco (`_DEFER`) y otra de abort
(`_DEFAB`). El primer error se ignora y la pasada se abandona; si Nextor lo reintenta, sale
el diálogo de MM con la página 2 del TPA, y con Retry se vuelve a leer al segmento. Si se
aborta (Abort en el diálogo; CTRL+STOP no corta `_RDDRV` ni `_GETCLUS`), se reponen la
página 2, las dos rutinas de MM y el DTA, y se sigue con la de abort de MM (`056Ah`). Con
la pila en la página 2 (alguna rutina de MM la pone ahí) no se cambia el segmento.

| Zona | Qué era | Qué va |
| --- | --- | --- |
| `3D07h-3D2Ah`, `3D60h-3DDDh`, `3DDFh-3E01h` | el lector de directorios por sectores de MM (solo FAT12), muerto: `3D5Dh` lo salta con un `JP 3E4Ah` | de la versión 1: el gancho del listado, tablas, rutinas pequeñas y las variables de un byte |
| `5CF4h-5FAEh` (+ variables hasta `5FBCh`) | detrás del final de MM.COM, sin usar | File info (versión 1); se añade al fichero |
| `5FBFh-600Fh` del fichero | lo pisan luego las marcas y los registros de MM | el arranque |
| `CB92h-D0EAh` | la pila de MM, que no baja de `D3xxh` | la pasada, la lista y la tabla (se copia del fichero) |
| un segmento del mapper | el último de los que MM se queda para copiar | la tabla (`8000h`, 256 × 32), el nombre que se junta, la conversión de caracteres, los clusters de la carpeta y 8 sectores |

No se tocan `3DDEh` ni `3E3Eh` (MM y MM.EXE los reescriben) ni `3D2Bh`-`3D5Fh` y
`3E03h`-`3E49h` (los llaman overlays de MM.EXE). Los sitios desviados:

| Dirección | Antes | Ahora |
| --- | --- | --- |
| `0100h` | `JP 5CC4h` | `JP start` |
| `586Fh` | `LD (HL),FFh` / `LD A,(F24Fh)` | `CALL takeseg` / `NOP` / `NOP` |
| `3E4Ah` | `LD HL,5FFFh` | `CALL lstart` |
| `3E88h` | `LD DE,C935h` | `JP hookfib` |
| `3E82h` | `LD HL,(3E8Ch)` | `JP pass` |
| `33BFh` | `CALL 1376h` | `CALL lstname` |
| `34C3h` | `CALL 36C4h` | `CALL prep` |
| `34D5h` | `CALL 13BAh` | `CALL tname` |
| `3547h` | `CALL 35C3h` | `CALL mydate` |

## Pruebas (openMSX, Philips NMS 8245 con 4 MB y Sunrise IDE)

Con Nextor 2.1.4 y con Nextor 3.0.0-beta2 (núcleo base de Konamiman con su driver Sunrise
IDE para Nextor 3, montado con N80 y mknexrom), en imágenes hechas con `MSXsdmaker.py
imagen` (FAT16 de 256 MB, clusters de 4 KB):

- una carpeta de 200 nombres de 32-53 caracteres, otra de 300 (MM se queda 257), la raíz
  (con la etiqueta de volumen) y una de casos raros: nombres de 7, 12, 13, 31, 32, 204 y 255
  caracteres, con acentos, japonés, `a.txt` en minúsculas (8.3 con los bits de NT, sin
  nombre largo), `Telnet.com`, carpetas con y sin nombre largo;
- las vistas de 1, 2, 3 y 5 columnas, File info en cada elemento, marcar, ordenar (las
  carpetas primero: MM mueve los registros), renombrar, borrar (MM no vuelve a listar),
  copiar, un listado con un patrón (`*.TXT`, puesto en memoria), entrar y salir de
  carpetas y volver de un programa cuatro veces seguidas (el segmento se libera y se vuelve
  a coger el mismo);
- un mapper de 128 KB (la lista sigue en 8.3 y File info lee el disco) y el arranque sin
  sitio en la página 3 (forzado: se queda como la versión 1);
- un error de disco en la pasada (un sector fuera del disco, el segundo error, Abort en el
  diálogo de MM: MM se recupera, vuelve a listar y sigue con su segmento) y CTRL+STOP
  pulsado durante la pasada;
- con puntos de vigilancia en `CB92h-D0EAh`: no escribe nadie más que el parche (y Nextor
  en el búfer de `_GETCLUS`); la pila no baja de `D3EAh` (Nextor 3, File info leyendo
  el disco) ni, con la tabla, de `D6E5h` (Nextor 3) y `D7D8h` (Nextor 2.1.4).

## La variante RC5

Multi Mente 2.07A+ RC5 es la compilación de la comunidad que reparte MSX Resource Center (el `MM.COM` en inglés de
la raíz del `MMv2.07Aplus-RC5.zip` interior; manual «patched FAT16 & Y2K»). Comparada con la 2.07_A:

- **Mismo código, mismas direcciones.** Salvo los 13 bytes que añade al final, todos los cambios conservan el tamaño.
  Los 8 sitios donde engancha este parche (`3E4Ah`, `3E88h`, `3E82h`, `33BFh`, `34C3h`, `34D5h`, `3547h`, `586Fh`) son
  idénticos a los de la 2.07_A, y las rutinas de MM que llama el parche (`1376h`, `13BAh`, `15A8h`, `164Eh`, `36C4h`,
  `35C3h`, `56E2h`...) están en el mismo sitio.
- **Qué cambia en la RC5** (desensamblado de la diferencia, 121 bloques): textos (cadena de versión `2.07A+`,
  diálogos), tablas de configuración y asociaciones del principio del fichero, el arreglo del reloj (año 2000: la
  rutina que pinta las cifras de `0D8Ah` y un envoltorio en `5CF0h` que llama a `15A8h`), el arranque (se quita la
  comprobación de turbo R de `5CC4h` y el byte que ponía en `0722h` queda fijo; `0100h` salta directo a `5783h`) y una
  protección de FAT16 (`wr[Y]ting` se ignora en FAT16; el manual dice que no se use Sort ni el Filer en FAT16). No es
  una adaptación a Nextor: el listado ya iba por la API de DOS 2 (`3D5Dh` salta a `3E4Ah`).
- **Lo que choca con el parche, y cómo se resuelve:**
  1. *El arranque.* La 2.07_A arranca en `5CC4h` y esa rutina acaba en `JP 5783h`; en la RC5 `0100h` ya salta a
     `5783h`. `MMSTART` vale `5783h` (`RC5 equ 1`, que `parchear.py` escribe en `variante.inc`).
  2. *El final del fichero.* La RC5 acaba en `5D00h` (la 2.07_A en `5CF3h`) y el código de File info (699 bytes) ya no
     cabe antes de `5FBFh` con sus 14 bytes de variables. En la RC5 el código va desde `5D00h` y las variables van en el
     relleno de `1Ah` que deja la RC5 en `5CC4h-5CCDh` y `5CEAh-5CEDh`; ninguna instrucción referencia esas direcciones
     (comprobado buscando `xx 5C` tras un código de operación de salto, carga o llamada). `5CD0h-5CDBh` (el despachador
     de FAT16, al que solo se llega desde `3D60h`), `5CE0h-5CE9h` y `5CF0h-5CFFh` (el arreglo del reloj, que **sí** se
     ejecuta) no se tocan: en el `.ips` no hay ni un byte entre `5CC0h` y `5CFFh`.
  3. *`3D60h`.* La RC5 puso ahí un `JP 5CD0h`, justo en el código muerto de MM que este parche sobrescribe
     (`3D60h-3DDDh`). Nadie salta a `3D60h` ni a `5CD0h` (ni en MM.COM ni en MM.EXE) y `3D5Dh` sigue siendo un `JP 3E4Ah`
     incondicional: queda sin ejecutarse, como en la 2.07_A. Se comprobó también en ejecución (ver más abajo).
- **Resultado:** el parche toca los mismos 14 tramos de la 2.07_A (arranque, 7 ganchos, las zonas muertas y la cola). El
  `MM_LFN_RC5.ips` pesa 2.417 bytes.

### Pruebas con la RC5 (banco `tests/openmsx/probar_mm.py`)

Mismo montaje (Philips NMS 8245, 4 MB, Sunrise IDE, imagen FAT16 de 256 MB hecha con `MSXsdmaker.py`), con la RC5
original y la parcheada y, como referencia, la 2.07_A original y la parcheada, con Nextor 2.1.1 (el kernel que trae
openMSX). Con Nextor 2.1.4 se repitió solo la lista y File info de todos los elementos de la RC5 parcheada (sin
fallos); con Nextor 3.0 la RC5 no se ha probado. Con los cuatro binarios:

- **Lista y File info** (`--escenario lista`, 12 elementos; con `--info-todos`, todos): en la RC5 parcheada salen los
  mismos nombres que en la 2.07_A parcheada, y los ficheros con solo 8.3 salen como siempre. La cabecera sigue diciendo
  `MM v2.07A+` y el reloj marca bien el año.
- **Interacción** (`--escenario interaccion`, 42 capturas por pasada, 10 comprobaciones mecánicas, 0 fallos en los
  cuatro): ordenar por nombre ascendente y descendente (carpetas primero; cada hueco sigue siendo de su fichero:
  comprobado por el tamaño de File info en 8 posiciones), marcar 3 ficheros y desmarcarlos, entrar en una carpeta con
  nombre largo y volver, volver 4 veces de `[X]ecom` (`ver`, un `HOLA.COM`, `dir`, `HOLA.COM`; la lista se repinta
  idéntica byte a byte en VRAM), borrar, copiar (lo copiado sale con el 8.3, como avisa el LEEME) y salir.
- **`CS MM`** (CS 3.11 con la 2.07_A, CS 3.12 con la RC5; el MM parcheado tiene 25.673 bytes): CS termina bien
  (`complete`), no cambia el tamaño ni trunca, y solo toca el bloque de configuración del principio (59 bytes entre
  `0108h` y `0328h` en la 2.07_A; 13 bytes entre `00FDh` y `02C8h` en la RC5), nada del código del parche. Después MM
  arranca y sigue enseñando nombres largos, con los mismos hashes de VRAM que sin CS. En este entorno CS no lanza MM
  al acabar (vuelve al prompt), también con el original.
- **Código «muerto»** (`--contar-ejecucion "3D60-3DDD 5CD0-5CFF"`, un punto de ruptura en cada instrucción, con los
  originales sin parche, durante el escenario entero): en `3D60h-3DDDh` el código de MM.COM no se ejecuta ni una vez ni
  en la 2.07_A ni en la RC5, ni tampoco `5CD0h`. Los aciertos que salen en esas direcciones (2 a 4 en `3D60h`, 123 a 145
  en `3DCDh`) son del `COMMAND2.COM` que `[X]ecom` carga en el TPA, y del `dir` de DOS al salir de MM. Cuidado: el resto
  de `5CD0h-5CFFh` **no** está muerto (en la 2.07_A, `5CD1h-5CEBh` corre una vez por cada vuelta de `[X]ecom`; en la RC5,
  `5CF0h-5CFFh` lee el reloj sin parar), pero ahí el parche no escribe nada.
- Límites del banco: va en SCREEN 7 y no hay forma de leer el texto de la pantalla, así que los nombres se verifican
  mirando las capturas; los controles mecánicos son hashes de VRAM, prompts de DOS y que no salga `Unrecognized command`.
  Dos diferencias entre versiones que no son del parche: al volver de un programa el cursor se queda donde estaba en la
  2.07_A y vuelve a `..\` en la RC5, que además repinta más despacio (pausas de 7-8 s emulados al borrar o copiar).
