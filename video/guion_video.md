# Guion del video (2:39)

Video para YouTube (la rúbrica pide de 1 a 3 min). Hay dos versiones en esta carpeta:

- `video_proyecto.mp4`: con narración sintetizada y subtítulos.
- `video_proyecto_sin_voz.mp4`: las mismas imágenes sin audio ni subtítulos, para grabar la narración con su propia
  voz siguiendo este guion (los tiempos ya están ajustados a las imágenes).

`subtitulos.srt` se puede subir a YouTube como archivo de subtítulos.

| Tiempo | Escena | Narración |
|---|---|---|
| 0:00–0:06 | Portada | Flujo laminar sobre un escalón descendente. Proyecto final de Mecánica de Fluidos. |
| 0:06–0:24 | El fenómeno | Un fluido viaja por un canal y encuentra un escalón: el canal se ensancha al doble. El fluido se frena, la presión sube, y el fluido lento junto a la pared no puede avanzar contra ese gradiente adverso. Se separa en la esquina, forma un remolino, y vuelve a tocar el piso en el punto de reacoplamiento. |
| 0:24–0:38 | Modelo: ecuaciones y supuestos | El modelo es flujo bidimensional, incompresible, newtoniano y laminar. Resolvemos continuidad y Navier Stokes en forma adimensional, con un solo parámetro: el número de Reynolds. Bajar la viscosidad es subir Reynolds. |
| 0:38–0:50 | Condiciones iniciales y de frontera | En la entrada imponemos el perfil parabólico de Poiseuille. En las paredes y en el escalón, no deslizamiento. En la salida, flujo desarrollado y presión cero. El fluido parte del reposo. |
| 0:50–1:07 | Método numérico | Cada paso de tiempo se resuelve en tres pasos. Uno: una velocidad de prueba sin presión, con Adams Bashforth. Dos: una ecuación de Poisson para la presión que hace cumplir la continuidad. Tres: corregir la velocidad con el gradiente de presión. |
| 1:07–1:12 | Demo en Jupyter: ejecutar | Así corremos el código en Jupyter. Los parámetros están al inicio. |
| 1:12–1:21 | Demo: recorrer el código | Cada función hace una tarea: la malla, la matriz de presión, las fronteras, la convección y difusión, y el ciclo de tres pasos. |
| 1:21–1:31 | Demo: resultado del caso base | El caso base, con Reynolds doscientos, converge en unos tres segundos. La masa se conserva, y el remolino mide cuatro punto nueve alturas de escalón. |
| 1:31–1:35 | Demo: cambiar Re a 400 | Probamos otro parámetro: Reynolds cuatrocientos. |
| 1:35–1:38 | Demo: corre (×3) | (sin narración) |
| 1:38–1:45 | Demo: resultado Re = 400 | Con menos viscosidad, el remolino crece a ocho punto tres alturas de escalón. |
| 1:45–2:00 | Simulación del arranque (tinta virtual) | Esta es la simulación del arranque, con tinta virtual. La capa de corte se enrolla en un vórtice que viaja aguas abajo. El remolino crece hasta su largo final, y el fluido gris queda atrapado girando: eso es la recirculación. |
| 2:00–2:12 | Efecto de la viscosidad (Re 100, 300, 600) | Al bajar la viscosidad el remolino se alarga: de dos punto ocho alturas de escalón en Reynolds cien, a diez en Reynolds seiscientos. Desde Reynolds cuatrocientos aparece un segundo remolino en el techo. |
| 2:12–2:23 | Malla y paso de tiempo | Al duplicar la malla, el resultado cambia menos de uno por ciento. El paso de tiempo no cambia el resultado mientras sea estable; en el límite de Courant, la solución explota. |
| 2:23–2:29 | Comparación con la literatura | Frente a la literatura, la diferencia es de dos por ciento o menos entre Reynolds doscientos y seiscientos. |
| 2:29–2:39 | Conclusiones | En resumen: resolvimos Navier Stokes, reprodujimos la separación, la recirculación y el reacoplamiento, y validamos el resultado. Gracias. |

Al subirlo a YouTube, poner el enlace nuevo en `reporte/reporte.md` (recuadro de la portada) y regenerar el PDF
con `python reporte/build_pdf.py`.

**Fuentes** (`fuentes/`): `grabar.js` graba JupyterLab con Playwright; `imagenes.py` hace la portada, la figura anotada
y el cierre; `voz.py` sintetiza la voz con espeak-ng + MBROLA (voz es1); `guion.py` tiene el texto; `hacer_video.py`
arma todo con ffmpeg.
