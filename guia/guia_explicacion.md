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

**A6. El problema de la presión y el método de proyección.** En incompresible no hay ecuación de estado para $p$. La presión
es "lo que haga falta" para que se cumpla continuidad. El método de Chorin lo resuelve en tres pasos:

1. $\mathbf u^*=\mathbf u^n+\Delta t\,[\nu\nabla^2\mathbf u-\text{convección}]$ (Navier–Stokes sin la presión).
2. Queremos $\mathbf u^{n+1}=\mathbf u^*-\Delta t\nabla p$ con $\nabla\cdot\mathbf u^{n+1}=0$. Aplica divergencia:
   $0=\nabla\cdot\mathbf u^*-\Delta t\nabla^2p\ \Rightarrow\ \nabla^2p=\nabla\cdot\mathbf u^*/\Delta t$ (**ecuación de Poisson**).
3. Con esa $p$, $\mathbf u^{n+1}=\mathbf u^*-\Delta t\nabla p$.

Si sumas los pasos 1 y 3 te queda exactamente Navier–Stokes discretizada en el tiempo con Euler.

**A7. Sistema lineal y LU.** La ecuación de Poisson discretizada da una ecuación por celda que liga cada $p$ con sus 4 vecinos:
un sistema $A\,p=b$ con 6000 incógnitas (malla de 300×20). $A$ es casi toda ceros (**dispersa**). La factorización LU es
eliminación gaussiana guardada: se hace una vez (porque $A$ no cambia) y en cada paso de tiempo sólo se sustituye.

**A8. Euler explícito y condición CFL.** $u^{n+1}=u^n+\Delta t\cdot(\text{lo que calculo con }u^n)$. Es estable sólo si en
un $\Delta t$ la información no viaja más de una celda: $\Delta t\le\Delta x/u_{max}$ (Courant–Friedrichs–Lewy). Hay otro
límite por la difusión, $\Delta t\le Re\,\Delta x^2/4$, pero aquí es mucho más grande.

**A9. GAMMA: cómo se estima un valor en la cara.** Para la convección necesitamos $u$ en las caras de la celda. El promedio de
los dos vecinos es preciso pero, con Euler explícito, inestable cuando la convección domina. Tomar el valor de donde viene el
flujo (*upwind*) es estable pero añade una viscosidad falsa ("difusión numérica"). Con `GAMMA = 0.5` se toma un punto
intermedio.

**A10. Estado estacionario.** Arrancamos del reposo y avanzamos en el tiempo hasta que la velocidad deja de cambiar
($\max|u^{n+1}-u^n|/\Delta t<10^{-5}$). Ese estado final es la solución estacionaria.

**A11. Reacoplamiento y esfuerzo cortante.** En la pared $\tau_w=\mu\,\partial u/\partial y$. Dentro del remolino $u<0$
cerca del piso, entonces $\tau_w<0$; después del remolino $\tau_w>0$. El punto donde $\tau_w=0$ es el reacoplamiento $x_r$.

**A12. Vorticidad.** $\omega=\partial v/\partial x-\partial u/\partial y$: qué tanto gira una partícula de fluido. Es
grande en la capa de corte entre el chorro rápido y el remolino lento.

<div style="page-break-before: always"></div>

# B. El código, bloque por bloque

## B0. Librerías

| Línea | Qué hace |
|---|---|
| `import numpy as np` | Arreglos (matrices) y operaciones sobre arreglos completos sin `for`. |
| `import scipy.sparse as sps` | Matrices dispersas: sólo guardan los números distintos de cero. |
| `import scipy.sparse.linalg as spla` | Resolver $Ax=b$ con matrices dispersas (aquí: LU). |
| `import matplotlib.pyplot as plt` | Gráficas. |
| `import matplotlib.patches as patches` | Para dibujar el rectángulo del escalón. |
| `from matplotlib.animation import ...` | Animaciones y guardarlas como GIF. |
| `from IPython.display import HTML, display` | Mostrar la animación dentro del notebook. |
| `FIG = Path("figures"); FIG.mkdir(...)` | Carpeta para guardar figuras (se crea si no existe). |

## B1. Parámetros

| Línea | Qué hace |
|---|---|
| `RE = 200` | Número de Reynolds del caso base. Es lo que se cambia en la demo. |
| `NY = 20` | Celdas en la altura. El ancho de celda es `dx = 1/20 = 0.05`. |
| `L = 15.0` | Largo del canal después del escalón, en alturas. Debe ser mayor que el remolino. |
| `H = 1.0; S = 0.5; U = 1.0` | Altura del canal, del escalón y velocidad media (adimensionales). |
| `GAMMA = 0.5` | Mezcla promedio/upwind para la convección (A9). |

## B2. Malla: `crear_malla(NY, L)`

| Línea | Qué hace |
|---|---|
| `dx = H / NY` | Lado de cada celda cuadrada. |
| `NX = round(L / dx)` | Cuántas celdas caben a lo largo (300 para L = 15). |
| `x_p = (np.arange(NX) + 0.5) * dx` | `arange(NX)` = 0, 1, …, NX−1. Sumar 0.5 y multiplicar por dx da los **centros** de celda: 0.025, 0.075, … (ahí vive $p$). |
| `y_p = ...` | Lo mismo en $y$. |
| `x_u = np.arange(NX + 1) * dx` | Las NX+1 **caras** verticales: 0, 0.05, …, L (ahí vive $u$). |
| `return {...}` | Devuelve todo en un diccionario `m` para no pasar muchas variables. |

`perfil_entrada(y)`:

| Línea | Qué hace |
|---|---|
| `eta = (y - S) / (H - S)` | Coordenada normalizada del canal de entrada: 0 en el borde del escalón, 1 en el techo. |
| `np.where(y > S, 6*U*eta*(1-eta), 0.0)` | Arriba del escalón, parábola de Poiseuille; frente al escalón, 0 (es pared). El 6 sale de pedir velocidad media $U$: $\int_0^1 6\eta(1-\eta)\,d\eta=1$. El máximo es $1.5U$ en $\eta=0.5$. |

## B3. Matriz de presión: `matriz_presion(NX, NY, dx)`

Para cada celda escribimos el laplaciano de 5 puntos igualado a $b$:
$(p_E-p_P)+(p_W-p_P)+(p_N-p_P)+(p_S-p_P)=b\,\Delta x^2$. Cada término es "el flujo de presión" por una cara.

| Línea | Qué hace |
|---|---|
| `N = NX * NY` | Número de incógnitas = número de celdas. |
| `A = sps.lil_matrix((N, N))` | Matriz N×N vacía, en un formato fácil de llenar entrada por entrada. |
| `for i ... for j ...` | Recorre todas las celdas. |
| `k = i * NY + j` | Numera la celda (i, j) como una lista: primero toda la columna i = 0, luego i = 1, etc. El vecino de arriba es `k+1` y el de la derecha `k+NY`. |
| `if i < NX-1: A[k,k+NY] = 1; A[k,k] -= 1` | Término $(p_E-p_P)$: +1 al vecino, −1 a la diagonal. |
| `else: A[k,k] -= 2` | Última columna: a la derecha está la salida con $p=0$ en la cara, que está a **media** celda: $(0-p_P)/(\Delta x/2)$ → coeficiente −2. |
| `if i > 0: ...` | Vecino izquierdo. Si `i == 0`, a la izquierda está la entrada/escalón con $\partial p/\partial x=0$: ese término es cero y simplemente no se suma. |
| `if j < NY-1` / `if j > 0` | Vecinos de arriba/abajo. En techo y piso $\partial p/\partial y=0$, igual que antes. |
| `A = A.tocsc() / dx**2` | Divide entre $\Delta x^2$ y cambia a un formato rápido para cálculos. |
| `return spla.splu(A)` | Factorización LU. Devuelve un objeto con `.solve(b)` que resuelve $Ap=b$ en milisegundos. |

## B4. Condiciones de frontera: `fronteras(u, v, u_entrada)`

Forma de los arreglos: `u` es (NX+1)×(NY+2): NX+1 caras en $x$ y NY celdas en $y$ más una fantasma abajo y otra
arriba. `v` es (NX+2)×(NY+1): una fantasma a la izquierda y otra a la derecha.
**Índices de Python:** `0` es el primero, `-1` el último, `-2` el penúltimo, `1:-1` "todos menos el primero y el último".

| Línea | Qué hace |
|---|---|
| `u[0, 1:-1] = u_entrada` | Primera cara (x = 0), celdas reales: el perfil parabólico (0 frente al escalón). |
| `v[0, :] = -v[1, :]` | Columna fantasma a la izquierda: espejo, para que $v=0$ en $x=0$ (A5). |
| `u[:, 0] = -u[:, 1]` | Fila fantasma bajo el piso: espejo → $u=0$ en el piso (no deslizamiento). |
| `u[:, -1] = -u[:, -2]` | Igual en el techo. |
| `v[:, 0] = 0.0; v[:, -1] = 0.0` | $v$ vive justo sobre piso y techo, así que se pone 0 directamente (no atraviesa la pared). |
| `v[-1, :] = v[-2, :]` | Salida: copiar el vecino es $\partial v/\partial x=0$. |

## B5. Convección y difusión

`valor_en_cara(f_izq, f_der, vel)`:
`0.5*(f_izq + f_der) - 0.5*GAMMA*np.sign(vel)*(f_der - f_izq)`.
Con GAMMA = 0 es el promedio. Con GAMMA = 1 y `vel > 0` da `f_izq` (el valor de donde viene el flujo); con `vel < 0` da
`f_der`. `np.sign` devuelve +1 o −1.

`aceleracion_u(u, v, nu, dx)` calcula $\nu\nabla^2u-\partial(uu)/\partial x-\partial(vu)/\partial y$ en **todas** las caras
interiores a la vez (sin `for`; NumPy opera con bloques del arreglo):

| Línea | Qué hace |
|---|---|
| `P = u[1:-1, 1:-1]` | Bloque de todos los puntos interiores. |
| `E, W = u[2:, 1:-1], u[:-2, 1:-1]` | El mismo bloque corrido una posición a la derecha (este) o izquierda (oeste). |
| `N, Sur = u[1:-1, 2:], u[1:-1, :-2]` | Corrido arriba (norte) o abajo (sur). |
| `difusion = nu*(E+W+N+Sur-4*P)/dx**2` | Laplaciano de 5 puntos (A2) por la viscosidad. |
| `u_e, u_w = 0.5*(P+E), 0.5*(W+P)` | Velocidad que atraviesa la cara este y la oeste del volumen de control de $u$. |
| `v_n = 0.5*(v[1:-2,1:] + v[2:-1,1:])` | Velocidad vertical en la cara norte: promedio de las dos $v$ vecinas (izquierda y derecha) de la malla escalonada. |
| `v_s = ...` | Lo mismo en la cara sur. |
| `conveccion = (u_e*cara_e - u_w*cara_w)/dx + (v_n*cara_n - v_s*cara_s)/dx` | $\partial(uu)/\partial x+\partial(vu)/\partial y$ como "lo que sale menos lo que entra" (A3): velocidad que cruza la cara × valor de $u$ en esa cara. |
| `return difusion - conveccion` | Todo el lado derecho de Navier–Stokes **excepto** la presión. |

`aceleracion_v` es lo mismo para la ecuación de $y$, con los papeles de $u$ y $v$ intercambiados.

## B6. El ciclo en el tiempo: `simular(...)`

| Línea | Qué hace |
|---|---|
| `nu = 1.0 / Re` | Viscosidad adimensional (A1). |
| `m = crear_malla(NY, L)` | Arma la malla. |
| `dt = 0.5 * dx / 1.5` | Mitad del límite CFL con $u_{max}=1.5$ (A8). Para NY = 20: 0.0167. |
| `resolver_p = matriz_presion(...)` | Arma y factoriza la matriz de Poisson una sola vez. |
| `u = np.zeros(...); v = np.zeros(...)` | Condición inicial: reposo. |
| `fronteras(u, v, u_entrada)` | Impone la entrada y las paredes desde el inicio. |
| `while t < t_max:` | Avanza paso a paso. |
| `u_viejo = u.copy()` | Guarda $u^n$ para medir cuánto cambió. |
| **Paso 1** `u_est[1:-1,1:-1] += dt*aceleracion_u(...)` | Euler: $u^*=u^n+\Delta t\,(\text{difusión}-\text{convección})$. |
| `u_est[-1,1:-1] = u_est[-2,1:-1]` | Salida: $\partial u/\partial x=0$. |
| **Paso 2** `div = (u_est[1:]-u_est[:-1] + v_est[:,1:]-v_est[:,:-1])/dx` | Divergencia en cada celda: (sale por la derecha − entra por la izquierda) + (sale por arriba − entra por abajo). Es lo que "sobra" o "falta" de masa. |
| `p = resolver_p.solve((div/dt).ravel()).reshape(NX, NY)` | Resuelve $\nabla^2p=\nabla\cdot u^*/\Delta t$. `ravel` hace la matriz una lista (vector $b$) y `reshape` la regresa a matriz. |
| **Paso 3** `u[1:-1,1:-1] -= dt*(p[1:]-p[:-1])/dx` | $u=u^*-\Delta t\,\partial p/\partial x$; cada cara usa la presión de sus dos celdas (malla escalonada). |
| `u[-1,1:-1] -= dt*(0.0-p[-1])/(dx/2)` | En la cara de salida la presión es 0 y el centro de la última celda está a $\Delta x/2$. |
| `v[1:-1,1:-1] -= dt*(p[:,1:]-p[:,:-1])/dx` | Igual para $v$. |
| `fronteras(u, v, u_entrada)` | Actualiza las fantasmas con las velocidades nuevas. |
| `cambio = np.max(np.abs(u-u_viejo))/dt` | Qué tan rápido cambia todavía el flujo (≈ $\partial u/\partial t$ máximo). |
| `if not np.isfinite(cambio) or cambio > 1e3` | Si aparece infinito/NaN o crece mucho, la solución explotó (Δt demasiado grande). |
| `if cambio < tol and t > 5` | Estado estacionario: se detiene. `t > 5` evita parar al principio. |
| `r = dict(...)` | Junta todo el resultado en un diccionario. |
| `r["xr"] = reacoplamiento(r)` | Calcula el largo del remolino. |

## B7. Resultados

`reacoplamiento(r)`:

| Línea | Qué hace |
|---|---|
| `u_piso = r["u"][:, 1]` | $u$ en la primera fila de celdas sobre el piso. Como $u_{pared}=0$, su signo es el de $\tau_w=\mu\,u/(\Delta y/2)$ (A11). |
| `i_min = np.argmin(u_piso)` | Posición del flujo de regreso más fuerte (centro del remolino). |
| `for i in range(i_min, ...)` y `if u_piso[i] < 0 <= u_piso[i+1]` | Busca aguas abajo el primer cambio de signo de − a +. Empezar en `i_min` evita confundirse con un remolino diminuto en la esquina del escalón. |
| `return x[i] - u_piso[i]*(x[i+1]-x[i])/(u_piso[i+1]-u_piso[i])` | Interpolación lineal: el punto entre los dos nodos donde la recta cruza cero. |

`burbuja_superior(r)`: `np.where(r["u"][:, -2] < 0)[0]` da los índices donde la $u$ junto al techo es negativa; el primero
y el último son inicio y fin del remolino superior.

`velocidad_en_centros(r)`: promedia las dos $u$ (izquierda/derecha) y las dos $v$ (abajo/arriba) de cada celda para tener
todo en el mismo punto y poder graficar.

`divergencia_maxima(r)`: la misma divergencia del paso 2 con la velocidad final. Debe dar ~$10^{-15}$ (cero de la computadora).

## B8. Gráficas

* `graficar_campos`: `contourf` colorea la magnitud $\sqrt{u^2+v^2}$ (`np.hypot`); `streamplot` dibuja líneas de corriente;
  la vorticidad es $\partial v/\partial x-\partial u/\partial y$ con diferencias centradas
  $(f_{i+1}-f_{i-1})/(2\Delta x)$; la línea roja punteada marca $x_r$.
* `graficar_perfiles`: en cada estación $x_s$ dibuja la curva $x_s+0.8\,u(y)$, o sea el perfil "parado" en esa posición.
* `animar`: toma las fotos guardadas cada 15 pasos y dibuja un cuadro por foto.
* En 5.1, `contourf(..., uc.T, levels=[-10, 0], colors="red")` pinta de rojo donde $u<0$ (flujo de regreso). `.T` transpone
  porque `contourf` quiere las filas en $y$.
* El esfuerzo cortante en el piso es `nu * u[:,1] / (0.5*dx)`: $\nu\,\partial u/\partial y$ con $u_{pared}=0$ a media celda.

<div style="page-break-before: always"></div>

# C. Preguntas probables y respuestas cortas

**¿Por qué no se usa la presión en el paso 1?** Porque no la conocemos: es la que hace falta para que se cumpla continuidad.
Se calcula en el paso 2 justo para eso.

**¿De dónde sale la ecuación de Poisson?** De aplicar divergencia a $u^{n+1}=u^*-\Delta t\nabla p$ y pedir
$\nabla\cdot u^{n+1}=0$.

**¿Qué pasa si aumento Δt?** Mientras cumpla CFL, se llega al mismo resultado en menos pasos. Arriba de $\Delta x/u_{max}$
la solución explota (en el notebook: Δt = 0.045 explota en ~20 pasos).

**¿Por qué crece el remolino al bajar la viscosidad?** El chorro transmite su momento hacia el piso por difusión viscosa;
con menos viscosidad eso tarda más mientras la convección lo lleva más lejos, así que se vuelve a pegar más adelante.

**¿Por qué se separa el flujo?** Al ensancharse el canal el fluido se frena y la presión sube (gradiente adverso). El fluido
junto a la pared es lento y no tiene inercia para avanzar contra ese aumento de presión, así que se despega.

**¿Por qué aparece un remolino arriba para Re ≥ 400?** El gradiente adverso también actúa sobre la capa límite del techo; con
poca viscosidad ésta también se separa.

**¿Cómo sabes que el resultado es correcto?** (1) La divergencia final es ~$10^{-15}$. (2) Al refinar la malla el resultado
converge. (3) Coincide con la literatura con diferencias menores a 3.5 %.

**¿Qué condición de salida usaste y por qué?** $\partial u/\partial x=0$ y $p=0$: suponemos que el flujo ya está
desarrollado (parábola) y fijamos la referencia de presión. Por eso el canal debe ser más largo que el remolino.

**¿Por qué la entrada es una parábola?** Es el perfil de Poiseuille, la solución exacta de Navier–Stokes para un canal
largo: suponemos que el fluido viene de un canal donde ya se desarrolló.

**¿Por qué la velocidad máxima final es 0.75?** Conservación de masa: el caudal es el mismo ($U\cdot h$) pero el canal
mide el doble, así que la velocidad media baja a la mitad (0.5) y el máximo de la parábola es 1.5 × 0.5 = 0.75.

**¿Qué es GAMMA?** Cómo se estima la velocidad en la cara de una celda para la convección: promedio de los vecinos
(preciso pero inestable) o el valor de donde viene el flujo (estable pero difusivo). Usamos una mezcla, 0.5.

**¿Por qué malla escalonada?** Para que la fuerza de presión sobre cada velocidad use dos presiones vecinas directas y no
aparezcan oscilaciones en zig-zag de la presión.

**¿Qué es el número de Reynolds aquí?** $Re=UH/\nu$ con $U$ la velocidad media de entrada y $H$ la altura del canal después
del escalón (que es el doble de la altura de entrada, igual que en Armaly et al. y Gartling).
