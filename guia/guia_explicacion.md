---
title: "Guía de estudio: el código del escalón descendente, línea por línea"
subtitle: "Para exponer el proyecto sabiendo hasta Navier–Stokes"
lang: es
---

Esta guía explica **cada línea** del notebook `escalon_descendente.ipynb`. Está en el mismo orden que el código.
Primero vienen los conceptos nuevos que aparecen después de Navier–Stokes (sección A); después, el código bloque por
bloque (sección B); al final, preguntas que probablemente haga el profesor, con su respuesta (sección C).

# A. Conceptos que necesitas (todo parte de Navier–Stokes)

**A1. Número de Reynolds.** Si en Navier–Stokes divides longitudes entre $H$, velocidades entre $U$ y presión entre
$\rho U^2$, la ecuación queda igual pero con $\nu$ sustituida por $1/Re$, con $Re = UH/\nu$. Significa
"inercia / viscosidad". Por eso en el código $U = H = 1$ y `nu = 1/Re`: **cambiar Re es cambiar la viscosidad**.

**A2. Discretizar.** La computadora no sabe derivar; sabe restar. Partimos el dominio en celdas de lado $\Delta x$ y usamos
la definición de derivada sin el límite:
$$\frac{\partial u}{\partial x}\approx\frac{u_{i+1}-u_i}{\Delta x},\qquad
\frac{\partial^2u}{\partial x^2}\approx\frac{u_{i+1}-2u_i+u_{i-1}}{\Delta x^2}.$$
La segunda sale de restar dos primeras derivadas. El **laplaciano** en 2D con celdas cuadradas es
$\nabla^2u\approx(u_E+u_W+u_N+u_S-4u_P)/\Delta x^2$ ("5 puntos").

**A3. Forma conservativa.** $u\,\partial u/\partial x+v\,\partial u/\partial y = \partial(uu)/\partial x+\partial(vu)/\partial y$
cuando $\partial u/\partial x+\partial v/\partial y=0$ (desarrolla la derivada del producto y usa continuidad). La segunda forma
se lee como "lo que sale por una cara menos lo que entra por la otra", y así el momento no se crea ni se pierde por error numérico.

**A4. Malla escalonada.** $p$ en el centro de cada celda; $u$ en las caras izquierda/derecha; $v$ en las caras de
abajo/arriba (ver figura del notebook). Ventaja: la velocidad de una cara queda **entre dos presiones**, y la fuerza
$-\partial p/\partial x$ sobre ella es simplemente $-(p_{der}-p_{izq})/\Delta x$. Si todo estuviera en el mismo punto, la
presión podría oscilar en zig-zag sin que el método lo notara.

**A5. Celda fantasma.** Una fila de celdas inventadas fuera de la pared. Si en la pared queremos $u=0$ y la pared queda
justo a la mitad entre la celda fantasma y la primera celda real, basta poner $u_{fantasma}=-u_{real}$: el promedio de los dos
es cero.

**A6. El escalón como bloque sólido.** La malla es un rectángulo completo $[-2, L]\times[0, 1]$; las celdas con $x<0$ y
$y<S$ se marcan como sólidas (`solido = True`). Ahí la velocidad es cero y la presión no se calcula. Sus paredes (la tapa y la
cara vertical) se tratan igual que el piso: velocidad normal cero y celda fantasma para la tangencial.

**A7. El problema de la presión y el método de proyección.** En incompresible no hay ecuación de estado para $p$. La presión
es "lo que haga falta" para que se cumpla continuidad. El método de Chorin lo resuelve en tres pasos:

1. $\mathbf u^*=\mathbf u^n+\Delta t\,A$, con $A=\nu\nabla^2\mathbf u-\text{convección}$ (Navier–Stokes sin la presión).
2. Queremos $\mathbf u^{n+1}=\mathbf u^*-\Delta t\nabla p$ con $\nabla\cdot\mathbf u^{n+1}=0$. Aplica divergencia:
   $0=\nabla\cdot\mathbf u^*-\Delta t\nabla^2p\ \Rightarrow\ \nabla^2p=\nabla\cdot\mathbf u^*/\Delta t$ (**ecuación de Poisson**).
3. Con esa $p$, $\mathbf u^{n+1}=\mathbf u^*-\Delta t\nabla p$.

Si sumas los pasos 1 y 3 te queda exactamente Navier–Stokes discretizada en el tiempo.

**A8. Sistema lineal y LU.** La ecuación de Poisson discretizada da una ecuación por celda que liga cada $p$ con sus 4 vecinos:
un sistema $A\,p=b$ con 6800 incógnitas (malla de 340×20). $A$ es casi toda ceros (**dispersa**). La factorización LU es
eliminación gaussiana guardada: se hace una vez (porque $A$ no cambia) y en cada paso de tiempo sólo se sustituye.

**A9. Convección por promedio.** Para la convección necesitamos $u$ en las caras de la celda; usamos el **promedio** de los dos
vecinos. Es lo más simple y lo más preciso: el error es proporcional a $\Delta x^2$ (al duplicar la malla, el error baja ~4 veces).

**A10. Avance en el tiempo: Euler y Adams–Bashforth.** Euler es $u^{n+1}=u^n+\Delta t\,A^n$: usa la pendiente del **inicio** del
paso, como si fuera constante todo el paso. Con convección por promedio eso amplifica un poco los errores en cada paso y la
solución explota (en el notebook, a los 706 pasos). Adams–Bashforth usa la pendiente a la **mitad** del paso, estimada con una
recta que pasa por la pendiente actual y la anterior:
$$A^{n+1/2}\approx A^n+\tfrac12(A^n-A^{n-1})=\tfrac32A^n-\tfrac12A^{n-1}.$$
Cuesta lo mismo (la $A$ anterior ya estaba calculada) y es estable.

**A11. Condición CFL.** En un $\Delta t$ la información no debe viajar más de una celda: $\Delta t\le\Delta x/u_{max}$
(Courant–Friedrichs–Lewy). Usamos la mitad. En el notebook, con el límite completo, explota en 36 pasos.

**A12. Estado estacionario.** Arrancamos del reposo y avanzamos en el tiempo hasta que la velocidad deja de cambiar
($\max|u^{n+1}-u^n|/\Delta t<10^{-4}$). Ese estado final es la solución estacionaria.

**A13. Reacoplamiento y esfuerzo cortante.** En la pared $\tau_w=\mu\,\partial u/\partial y$. Dentro del remolino $u<0$
cerca del piso, entonces $\tau_w<0$; después del remolino $\tau_w>0$. El punto donde $\tau_w=0$ es el reacoplamiento $x_r$.

**A14. Vorticidad.** $\omega=\partial v/\partial x-\partial u/\partial y$: qué tanto gira una partícula de fluido. Es
grande en la capa de corte entre el chorro rápido y el remolino lento.

**A15. Tinta virtual (partículas trazadoras).** Una partícula sin masa se mueve con el fluido: $d\mathbf x/dt=\mathbf u$. Es una
ecuación de "posición = posición + velocidad × tiempo", la misma que en cinemática. Como la velocidad sólo se conoce en los
nodos, se **interpola** (promedio pesado de los 4 nodos más cercanos). Para avanzar se usa Runge–Kutta 2: primero se calcula
dónde estaría la partícula a medio paso y se usa la velocidad de ese punto.

<div style="page-break-before: always"></div>

# B. El código, bloque por bloque

**Índices de Python:** `0` es el primero, `-1` el último, `-2` el penúltimo, `1:-1` "todos menos el primero y el último",
`:I0` "desde el inicio hasta antes de I0". `a[:, None]` convierte una lista en columna para comparar contra una fila.

## B0. Librerías

| Línea | Qué hace |
|---|---|
| `import numpy as np` | Arreglos (matrices) y operaciones sobre arreglos completos sin `for`. |
| `import scipy.sparse as sps` | Matrices dispersas: sólo guardan los números distintos de cero. |
| `import scipy.sparse.linalg as spla` | Resolver $Ax=b$ con matrices dispersas (aquí: LU). |
| `import matplotlib.pyplot as plt` / `patches` | Gráficas / el rectángulo del escalón. |
| `import subprocess` | Llamar al programa `ffmpeg` (hace los videos). |
| `from IPython.display import Video, display` | Mostrar el video dentro del notebook. |
| `try: import imageio_ffmpeg ...` | Si está instalado `imageio-ffmpeg`, usa su copia de ffmpeg; si no, la del sistema. |
| `FIG = Path("figures"); FIG.mkdir(...)` | Carpeta para guardar figuras (se crea si no existe). |

## B1. Parámetros

| Línea | Qué hace |
|---|---|
| `RE = 200` | Número de Reynolds del caso base. Es lo que se cambia en la demo. |
| `NY = 20` | Celdas en la altura. El ancho de celda es `dx = 1/20 = 0.05`. |
| `L = 15.0` | Largo del canal después del escalón, en alturas. Debe ser mayor que el remolino. |
| `HACER_VIDEOS = True` | Con `False` se saltan los videos (más rápido para la demo). |
| `H, S, U = 1.0, 0.5, 1.0` | Altura del canal, del escalón y velocidad media (adimensionales). |
| `LI = 2.0` | Largo del canal de entrada antes del escalón. |
| `CFL = 0.5` | Usamos la mitad del $\Delta t$ máximo estable (A11). |

## B2. Malla: `crear_malla(NY, L)`

| Línea | Qué hace |
|---|---|
| `dx = H / NY` | Lado de cada celda cuadrada. |
| `NX = round((LI + L) / dx)` | Celdas a lo largo, contando el canal de entrada (340 para L = 15). |
| `x_p = (np.arange(NX) + 0.5) * dx - LI` | `arange(NX)` = 0, 1, …, NX−1. Sumar 0.5 y multiplicar por dx da los **centros** de celda; restar `LI` hace que $x=0$ quede en el escalón. Ahí vive $p$. |
| `y_p = (np.arange(NY) + 0.5) * dx` | Centros en $y$. |
| `x_u = np.arange(NX + 1) * dx - LI` | Las NX+1 **caras** verticales, de $-2$ a $L$. Ahí vive $u$. |
| `solido = (x_p[:, None] < 0) & (y_p[None, :] < S)` | Tabla NX×NY de verdadero/falso: verdadero en las celdas del escalón (A6). |
| `I0 = round(LI / dx)` | Índice de la cara $x=0$ (la cara del escalón) en `x_u`: 40. |
| `J0 = round(S / dx)` | Cuántas filas de celdas quedan bajo $y=S$: 10. |

`perfil_entrada(y)`:

| Línea | Qué hace |
|---|---|
| `eta = (y - S) / (H - S)` | Coordenada del canal de entrada: 0 en la tapa del escalón, 1 en el techo. |
| `np.where(y > S, 6*U*eta*(1-eta), 0.0)` | Arriba del escalón, parábola de Poiseuille; abajo, 0. El 6 sale de pedir velocidad media $U$: $\int_0^1 6\eta(1-\eta)\,d\eta=1$. El máximo es $1.5U$ en $\eta=0.5$. |

## B3. Matriz de presión: `matriz_presion(m)`

Para cada celda con fluido escribimos el laplaciano de 5 puntos igualado a $b$:
$(p_E-p_P)+(p_W-p_P)+(p_N-p_P)+(p_S-p_P)=b\,\Delta x^2$. Cada término es "el flujo de presión" por una cara.

| Línea | Qué hace |
|---|---|
| `A = sps.lil_matrix((NX*NY, NX*NY))` | Matriz vacía, una fila por celda, en un formato fácil de llenar. |
| `for i ... for j ...` | Recorre todas las celdas. |
| `k = i * NY + j` | Numera la celda (i, j) como una lista: primero toda la columna i = 0, luego i = 1, etc. El vecino (vi, vj) es `vi*NY + vj`. |
| `if solido[i, j]: A[k, k] = 1; continue` | Celda del escalón: ecuación trivial "p = 0" y se pasa a la siguiente. |
| `for vi, vj in [(i+1, j), (i-1, j), (i, j+1), (i, j-1)]` | Los 4 vecinos: derecha, izquierda, arriba, abajo. |
| `if vi == NX: A[k, k] -= 2` | A la derecha de la última columna está la salida, con $p=0$ en la cara, que está a **media** celda: $(0-p_P)/(\Delta x/2)$ → coeficiente −2. |
| `elif vi >= 0 and 0 <= vj < NY and not solido[vi, vj]` | El vecino existe y tiene fluido: término $(p_{vec}-p_P)$ → +1 al vecino, −1 a la diagonal. |
| (si no se cumple ninguno) | El vecino es pared, entrada o escalón, donde $\partial p/\partial n=0$: ese término vale cero y no se suma. |
| `spla.splu(A.tocsc() / dx**2, permc_spec="MMD_AT_PLUS_A")` | Divide entre $\Delta x^2$, cambia a formato rápido y factoriza (LU). Devuelve un objeto con `.solve(b)`. `permc_spec` elige en qué orden se eliminan las incógnitas: con el orden MMD la LU tiene menos "relleno" (entradas nuevas distintas de cero) y cada solución es ~2 veces más rápida, con el mismo resultado. |

## B4. Condiciones de frontera: `fronteras(u, v, u_entrada, m)`

Forma de los arreglos: `u` es (NX+1)×(NY+2): NX+1 caras en $x$ y NY celdas en $y$ más una fantasma abajo y otra
arriba. `v` es (NX+2)×(NY+1): una fantasma a la izquierda y otra a la derecha. Por eso la fila de celdas `j` está en
`u[:, j+1]` y la columna `i` en `v[i+1, :]`.

| Línea | Qué hace |
|---|---|
| `u[0, 1:-1] = u_entrada` | Primera cara ($x=-2$): el perfil parabólico. |
| `v[0, :] = -v[1, :]` | Columna fantasma a la izquierda: espejo → $v=0$ en la entrada (A5). |
| `u[:I0+1, 1:J0+1] = 0.0` | Caras de $u$ dentro del escalón y en su cara vertical ($x=0$): velocidad cero (no la atraviesa). |
| `v[1:I0+1, :J0+1] = 0.0` | Caras de $v$ dentro del escalón y en su tapa ($y=S$): cero. |
| `u[:I0, J0] = -u[:I0, J0+1]` | La fila de $u$ justo bajo la tapa hace de fantasma: espejo → $u=0$ sobre la tapa. |
| `v[I0, 1:J0] = -v[I0+1, 1:J0]` | La columna de $v$ justo dentro del escalón hace de fantasma: espejo → $v=0$ en la cara vertical. |
| `u[:, 0] = -u[:, 1]` / `u[:, -1] = -u[:, -2]` | Fantasmas bajo el piso y sobre el techo: $u=0$ en las paredes. |
| `v[:, 0] = 0.0; v[:, -1] = 0.0` | $v$ vive justo sobre piso y techo, así que se pone 0 directamente. |
| `v[-1, :] = v[-2, :]` | Salida: copiar el vecino es $\partial v/\partial x=0$. |

## B5. Convección y difusión: `aceleracion_u(u, v, nu, dx)`

Calcula $\nu\nabla^2u-\partial(uu)/\partial x-\partial(vu)/\partial y$ en **todas** las caras interiores a la vez (sin `for`;
NumPy opera con bloques del arreglo):

| Línea | Qué hace |
|---|---|
| `P = u[1:-1, 1:-1]` | Bloque de todos los puntos interiores. |
| `E, W = u[2:, 1:-1], u[:-2, 1:-1]` | El mismo bloque corrido una posición a la derecha (este) o izquierda (oeste). |
| `N, Sur = u[1:-1, 2:], u[1:-1, :-2]` | Corrido arriba (norte) o abajo (sur). |
| `difusion = nu*(E+W+N+Sur-4*P)/dx**2` | Laplaciano de 5 puntos (A2) por la viscosidad. |
| `u_e, u_w = (P+E)/2, (W+P)/2` | $u$ en las caras este y oeste del volumen de control: promedio (A9). |
| `u_n, u_s = (P+N)/2, (Sur+P)/2` | $u$ en las caras norte y sur. |
| `v_n = (v[1:-2,1:] + v[2:-1,1:])/2` | Velocidad vertical que cruza la cara norte: promedio de las dos $v$ vecinas de la malla escalonada. |
| `v_s = ...` | Lo mismo en la cara sur. |
| `conveccion = (u_e*u_e - u_w*u_w)/dx + (v_n*u_n - v_s*u_s)/dx` | "Lo que sale menos lo que entra" (A3): velocidad que cruza la cara × $u$ en esa cara. |
| `return difusion - conveccion` | Todo el lado derecho de Navier–Stokes **excepto** la presión. |

`aceleracion_v` es lo mismo para la ecuación de $y$, con los papeles de $u$ y $v$ intercambiados.

## B6. El ciclo en el tiempo: `simular(...)`

| Línea | Qué hace |
|---|---|
| `nu = 1.0 / Re` | Viscosidad adimensional (A1). |
| `dt = CFL * dx / 1.5` | Mitad del límite CFL con $u_{max}=1.5$. Para NY = 20: 0.0167. |
| `resolver_p = matriz_presion(m)` | Arma y factoriza la matriz de Poisson una sola vez. |
| `u = np.zeros(...); v = np.zeros(...)` | Condición inicial: reposo. |
| `Au_ant = Av_ant = None` | Todavía no hay aceleración "anterior". |
| `while t < t_max:` | Avanza paso a paso. |
| `u_viejo = u.copy()` | Guarda $u^n$ para medir cuánto cambió. |
| **Paso 1** `Au, Av = aceleracion_u(...), aceleracion_v(...)` | Aceleración de ahora, $A^n$. |
| `if Au_ant is None or not ab2: Au_ant, Av_ant = Au, Av` | En el primer paso no hay anterior: se usa la actual (queda Euler). Con `ab2=False` se fuerza Euler siempre (para la prueba de 5.3). |
| `u_est[1:-1,1:-1] += dt*(1.5*Au - 0.5*Au_ant)` | Adams–Bashforth (A10): $u^*=u^n+\Delta t(\tfrac32A^n-\tfrac12A^{n-1})$. |
| `Au_ant, Av_ant = Au, Av` | La de ahora será la "anterior" en el siguiente paso. |
| `u_est[-1,1:-1] = u_est[-2,1:-1]` y `fronteras(...)` | Salida $\partial u/\partial x=0$ y paredes, antes de medir la divergencia. |
| **Paso 2** `div = (u_est[1:]-u_est[:-1] + v_est[:,1:]-v_est[:,:-1])/dx` | Divergencia en cada celda: (sale por la derecha − entra por la izquierda) + (sale por arriba − entra por abajo). Es lo que "sobra" o "falta" de masa. |
| `div[m["solido"]] = 0.0` | Dentro del escalón no hay nada que corregir. |
| `p = resolver_p.solve((div/dt).ravel()).reshape(NX, NY)` | Resuelve $\nabla^2p=\nabla\cdot u^*/\Delta t$. `ravel` hace la matriz una lista (vector $b$) y `reshape` la regresa a matriz. |
| **Paso 3** `u[1:-1,1:-1] -= dt*(p[1:]-p[:-1])/dx` | $u=u^*-\Delta t\,\partial p/\partial x$; cada cara usa la presión de sus dos celdas (malla escalonada). |
| `u[-1,1:-1] -= dt*(0.0-p[-1])/(dx/2)` | En la cara de salida la presión es 0 y el centro de la última celda está a $\Delta x/2$. |
| `v[1:-1,1:-1] -= dt*(p[:,1:]-p[:,:-1])/dx` | Igual para $v$. |
| `fronteras(u, v, ...)` | Vuelve a poner paredes, escalón y fantasmas con las velocidades nuevas. |
| `cambio = np.max(np.abs(u-u_viejo))/dt` | Qué tan rápido cambia todavía el flujo (≈ $\partial u/\partial t$ máximo). |
| `if fotos_cada and n % fotos_cada == 0: fotos.append(...)` | Guarda una "foto" del flujo cada cierto número de pasos (para el video). `float32` ocupa la mitad de memoria. |
| `if not np.isfinite(cambio) or cambio > 1e3` | Si aparece infinito/NaN o crece mucho, la solución explotó. |
| `if cambio < tol and t > 5` | Estado estacionario: se detiene. `t > 5` evita parar al principio. |
| `r["xr"] = reacoplamiento(m, u)` | Calcula el largo del remolino. |

## B7. Resultados

`reacoplamiento(m, u)`:

| Línea | Qué hace |
|---|---|
| `x = m["x_u"][m["I0"]:]`, `u_piso = u[m["I0"]:, 1]` | Sólo después del escalón: $u$ en la primera fila de celdas sobre el piso. Como $u_{pared}=0$, su signo es el de $\tau_w$ (A13). |
| `i_min = np.argmin(u_piso)` | Posición del flujo de regreso más fuerte (centro del remolino). |
| `for i in range(i_min, ...)` y `if u_piso[i] < 0 <= u_piso[i+1]` | Busca aguas abajo el primer cambio de signo de − a +. Empezar en `i_min` evita confundirse con un remolino diminuto en la esquina. |
| `return x[i] - u_piso[i]*(x[i+1]-x[i])/(u_piso[i+1]-u_piso[i])` | Interpolación lineal: el punto entre los dos nodos donde la recta cruza cero. |

`burbuja_superior(m, u)`: `np.where(u[:, -2] < 0)[0]` da los índices donde la $u$ junto al techo es negativa; el primero
y el último son inicio y fin del remolino superior.

`velocidad_en_centros(m, u, v)`: promedia las dos $u$ (izquierda/derecha) y las dos $v$ (abajo/arriba) de cada celda para
tener todo en el mismo punto y poder graficar. Dentro del escalón pone `NaN` ("no es un número"), que no se dibuja.

`vorticidad(m, u, v)`: `(v[1:, :] - v[:-1, :])/dx - (u[:, 1:] - u[:, :-1])/dx`. En cada **esquina** de celda hay dos $v$
(izquierda y derecha) y dos $u$ (abajo y arriba): restarlas da $\partial v/\partial x$ y $\partial u/\partial y$ directamente.

`divergencia_maxima(r)`: la misma divergencia del paso 2 con la velocidad final, en las celdas con fluido. Debe dar
~$10^{-14}$ (cero de la computadora).

## B8. Gráficas

* `graficar_campos`: `contourf` colorea la magnitud $\sqrt{u^2+v^2}$ (`np.hypot`); `streamplot` dibuja líneas de corriente
  (`nan_to_num` cambia los `NaN` del escalón por 0); la línea roja punteada marca $x_r$.
* `graficar_perfiles`: en cada estación $x_s$ dibuja la curva $x_s+0.8\,u(y)$, o sea el perfil "parado" en esa posición.
* En 5.1, `contourf(..., uc.T, levels=[-10, 0], colors="red")` pinta de rojo donde $u<0$ (flujo de regreso). `.T` transpone
  porque `contourf` quiere las filas en $y$.
* El esfuerzo cortante en el piso es `nu * u[I0:,1] / (0.5*dx)`: $\nu\,\partial u/\partial y$ con $u_{pared}=0$ a media celda.

## B9. Video: tinta virtual

`interpolar(f, x0, y0, dx, x, y)` (A15):

| Línea | Qué hace |
|---|---|
| `a, b = (x - x0)/dx, (y - y0)/dx` | Posición de cada partícula medida en celdas (por ejemplo, 12.3 celdas a la derecha). |
| `i = np.clip(a.astype(int), ...)` | Parte entera: el nodo de abajo a la izquierda (`clip` evita salirse del arreglo). |
| `a, b = a - i, b - j` | Parte fraccionaria: qué tan lejos está dentro de la celda, de 0 a 1. |
| `return (1-a)*(1-b)*f[i,j] + ...` | Promedio de los 4 nodos, cada uno pesado por qué tan cerca está la partícula. |

`class Tinta` guarda las posiciones `x, y` y un código de color `c` de todas las partículas:

| Parte | Qué hace |
|---|---|
| `ALTURAS = S + (H-S)*[...]` | Alturas de los 9 inyectores en la entrada. |
| `__init__`: `np.meshgrid(...)` | Llena el canal de partículas cada 0.025 (fluido inicial), quitando las del escalón. |
| `cuadro = (floor(x/0.25) + floor(y/0.25)) % 2` | 0 o 1 según la casilla del tablero de ajedrez: dos tonos de gris (`c` = −1 o −2). |
| `velocidad(...)` | Interpola $u$ y $v$; cada una con su propio origen porque viven en caras distintas de la malla escalonada. |
| `avanzar(u, v, dt)`: `sub = ceil(dt/0.025)` | Divide el intervalo entre fotos en sub-pasos pequeños. |
| `ux, uy = velocidad(..., x + h/2*ux, ...)` | Runge–Kutta 2: velocidad en el punto de medio paso. |
| `self.x = self.x + h*ux` | Mueve las partículas: posición + velocidad × tiempo. |
| `np.clip(...)` y `np.where((x<0)&(y<S), ...)` | No dejar que una partícula atraviese el piso, el techo o el escalón. |
| `np.append(...)` | Suelta 9 partículas nuevas en la entrada, una por inyector; `c` = número de inyector (+10 en los segundos impares, para el tono oscuro). |
| `vivas = self.x < self.x_max + 0.2` | Borra las que ya salieron de la vista. |
| `colores()` | Convierte el código `c` en color: colormap `turbo` por inyector, más oscuro si `c ≥ 10`, gris para el fluido inicial. |

`animar(casos, archivo, x_max)`: arma la figura de 1920×1080 (franjas de tinta, vorticidad si es un solo caso, y abajo
$x_r(t)$ y $u$ junto al piso). La función interna `cuadro(q)` dibuja cada cuadro: avanza la tinta hasta el tiempo de la
foto, redibuja el borde del remolino (`contour` de $u=0$), mueve la marca ▼ a $x_r$ y agrega un punto a la curva $x_r(t)$.
Las fotos se eligen para hacer **cámara lenta** al principio (todas hasta $t=10$, después una de cada 2 y luego una de cada 4).
Para que sea rápido, lo que no cambia (ejes, textos, escalón, barras de color) se dibuja **una sola vez** y se guarda como fondo (`copy_from_bbox`). En cada cuadro se restaura ese fondo, se redibujan sólo las partículas, las líneas y la vorticidad (`draw_artist`) y la imagen se manda directo a ffmpeg por una tubería (`subprocess.Popen`), que la comprime en MP4. Así el video tarda ~45 s en vez de ~4 min.

`mostrar_video` hace una copia de 960 px con ffmpeg y la incrusta en el notebook. `secuencia` usa la misma tinta para hacer
la figura de fotos fijas del reporte.

<div style="page-break-before: always"></div>

# C. Preguntas probables y respuestas cortas

**¿Por qué no se usa la presión en el paso 1?** Porque no la conocemos: es la que hace falta para que se cumpla continuidad.
Se calcula en el paso 2 justo para eso.

**¿De dónde sale la ecuación de Poisson?** De aplicar divergencia a $u^{n+1}=u^*-\Delta t\nabla p$ y pedir
$\nabla\cdot u^{n+1}=0$.

**¿Qué es Adams–Bashforth y por qué no Euler?** Euler usa la aceleración del inicio del paso; Adams–Bashforth estima la de
la mitad del paso con $\tfrac32A^n-\tfrac12A^{n-1}$. Con convección por promedio, Euler explota (lo mostramos: 706 pasos);
Adams–Bashforth no, y cuesta lo mismo.

**¿Qué pasa si aumento Δt?** Mientras sea estable, se llega al mismo resultado en menos pasos. En el límite CFL
($\Delta x/u_{max}=0.033$) la solución explota en 36 pasos.

**¿Por qué crece el remolino al bajar la viscosidad?** El chorro transmite su momento hacia el piso por difusión viscosa;
con menos viscosidad eso tarda más mientras la convección lo lleva más lejos, así que se vuelve a pegar más adelante.

**¿Por qué se separa el flujo?** Al ensancharse el canal el fluido se frena y la presión sube (gradiente adverso). El fluido
junto a la pared es lento y no tiene inercia para avanzar contra ese aumento de presión, así que se despega.

**¿Por qué aparece un remolino arriba para Re ≥ 400?** El gradiente adverso también actúa sobre la capa límite del techo; con
poca viscosidad ésta también se separa.

**¿Cómo sabes que el resultado es correcto?** (1) La divergencia final es ~$10^{-14}$. (2) Al duplicar la malla el resultado
cambia menos de 1 %. (3) Coincide con la literatura dentro de 2 % para Re de 200 a 600.

**¿Por qué hay un canal antes del escalón?** Para que el perfil de velocidad pueda deformarse antes de la esquina, como en un
canal real. Sin él la burbuja sale ~8 % más larga a Re = 200 (lo probamos) y no se compara bien con la literatura.

**¿Qué muestra la tinta del video?** Partículas que se mueven con el fluido. El fluido gris atrapado en la burbuja nunca sale:
eso es una zona de recirculación. La tinta de color muestra el vórtice de arranque y cómo el chorro rodea el remolino.

**¿Qué condición de salida usaste y por qué?** $\partial u/\partial x=0$ y $p=0$: suponemos que el flujo ya está
desarrollado (parábola) y fijamos la referencia de presión. Por eso el canal debe ser más largo que el remolino.

**¿Por qué la entrada es una parábola?** Es el perfil de Poiseuille, la solución exacta de Navier–Stokes para un canal
largo: suponemos que el fluido viene de un canal donde ya se desarrolló.

**¿Por qué la velocidad máxima final es 0.75?** Conservación de masa: el caudal es el mismo ($U\cdot h$) pero el canal
mide el doble, así que la velocidad media baja a la mitad (0.5) y el máximo de la parábola es 1.5 × 0.5 = 0.75.

**¿Por qué malla escalonada?** Para que la fuerza de presión sobre cada velocidad use dos presiones vecinas directas y no
aparezcan oscilaciones en zig-zag de la presión.

**¿Qué es el número de Reynolds aquí?** $Re=UH/\nu$ con $U$ la velocidad media de entrada y $H$ la altura del canal después
del escalón (que es el doble de la altura de entrada, igual que en Armaly et al. y Gartling).
