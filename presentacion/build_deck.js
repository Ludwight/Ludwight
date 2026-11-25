// Genera presentacion.pptx (12 diapositivas) con pptxgenjs, enfocada en el rigor matemático y el código.
// Uso (desde presentacion/):  npm install  →  python render_eqs.py  →  node build_deck.js  →  python transiciones.py presentacion.pptx
// Requiere que el notebook ya haya generado ../figures/*.png y ../figures/*.mp4.
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const AQUI = __dirname;
const FIG = path.join(AQUI, "..", "figures");
const EQ = path.join(AQUI, "eq");

const C = {
  navy: "0B1F3A", navy2: "1A3457", teal: "0E7C86", aqua: "7FD1D6", coral: "F26B3A",
  ink: "1E2A38", grey: "5B6878", paper: "F4F7FA", white: "FFFFFF", line: "D5DEE8", code: "EEF3F8",
};
const FUENTE_TITULO = "Cambria";
const FUENTE_TEXTO = "Calibri";
const FUENTE_CODIGO = "Courier New";

function tamanoPNG(archivo) {
  const b = fs.readFileSync(archivo);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}
function encajar(archivo, x, y, maxW, maxH) {
  const { w, h } = tamanoPNG(archivo);
  const k = Math.min(maxW / w, maxH / h);
  return { x: x + (maxW - w * k) / 2, y: y + (maxH - h * k) / 2, w: w * k, h: h * k };
}
const sombra = () => ({ type: "outer", blur: 10, offset: 3, angle: 90, color: "000000", opacity: 0.16 });

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Luis Antonio Pérez Hernández · Marco Antonio Navarrete Baños";
pres.title = "Flujo laminar sobre un escalón descendente";
pres.theme = { headFontFace: FUENTE_TITULO, bodyFontFace: FUENTE_TEXTO };

pres.defineSlideMaster({
  title: "CONTENIDO",
  background: { color: C.white },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.1, h: 0.9, valign: "middle",
      fontFace: FUENTE_TITULO, fontSize: 30, bold: true, color: C.navy, align: "left", margin: 0 }, text: "" } },
    { text: { text: "Flujo sobre un escalón descendente · Mecánica de Fluidos", options: { x: 0.6, y: 7.0, w: 9, h: 0.3,
      fontFace: FUENTE_TEXTO, fontSize: 10, color: "8A96A6", margin: 0 } } },
  ],
  slideNumber: { x: 12.2, y: 7.0, w: 0.5, h: 0.3, fontFace: FUENTE_TEXTO, fontSize: 10, color: "8A96A6", align: "right" },
});
pres.defineSlideMaster({
  title: "PORTADA",
  background: { color: C.navy },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.75, w: 6.2, h: 2.0, valign: "top",
      fontFace: FUENTE_TITULO, fontSize: 42, bold: true, color: C.white, margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "OSCURA",
  background: { color: C.navy },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.1, h: 0.9, valign: "middle",
      fontFace: FUENTE_TITULO, fontSize: 30, bold: true, color: C.white, align: "left", margin: 0 }, text: "" } },
  ],
});

let seccionActual = null;
function declarar(seccion) {
  if (seccion && seccion !== seccionActual) { pres.addSection({ title: seccion }); seccionActual = seccion; }
  return seccion;
}
function nueva(titulo, { seccion, oscura = false } = {}) {
  const s = pres.addSlide({ masterName: oscura ? "OSCURA" : "CONTENIDO", sectionTitle: declarar(seccion) });
  if (titulo) s.addText(titulo, { placeholder: "title" });
  return s;
}
function circulo(s, n, x, y, d = 0.45, color = C.teal) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color }, line: { type: "none" } });
  s.addText(String(n), { x, y, w: d, h: d, align: "center", valign: "middle", fontFace: FUENTE_TEXTO,
    fontSize: Math.round(d * 30), bold: true, color: C.white, margin: 0 });
}
function tarjeta(s, x, y, w, h, color = C.paper) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1, fill: { color },
    line: { type: "none" }, shadow: color === C.paper ? undefined : sombra() });
}
function imagen(s, archivo, x, y, maxW, maxH, conTarjeta = true) {
  const p = encajar(archivo, x, y, maxW, maxH);
  if (conTarjeta) tarjeta(s, p.x - 0.1, p.y - 0.1, p.w + 0.2, p.h + 0.2, C.white);
  s.addImage({ path: archivo, x: p.x, y: p.y, w: p.w, h: p.h });
  return p;
}
// Ecuación LaTeX (PNG de render_eqs.py), escalada para caber en maxW × maxH; devuelve su alto.
function eq(s, nombre, x, y, maxW, maxH = 1.0) {
  const archivo = path.join(EQ, nombre + ".png");
  const p = encajar(archivo, x, y, maxW, maxH);
  s.addImage({ path: archivo, x: p.x, y: p.y, w: p.w, h: p.h });
  return p.h;
}
function video(s, archivo, poster, x, y, w) {
  const h = w * 9 / 16;
  const cover = "data:image/png;base64," + fs.readFileSync(poster).toString("base64");
  s.addMedia({ type: "video", path: archivo, x, y, w, h, cover });
  return h;
}
function lista(s, items, x, y, w, h, tam = 14) {
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })),
    { x, y, w, h, fontFace: FUENTE_TEXTO, fontSize: tam, color: C.ink, valign: "top", paraSpaceAfter: 6, margin: 0 });
}
function texto(s, t, x, y, w, h, o = {}) {
  s.addText(t, Object.assign({ x, y, w, h, fontFace: FUENTE_TEXTO, fontSize: 14, color: C.ink, valign: "top", margin: 0 }, o));
}
// Bloque de código: cada línea es un párrafo; lo que sigue a '#' va en color de comentario.
function codigo(s, lineas, x, y, w, h, tam = 11) {
  const runs = [];
  lineas.forEach((ln, i) => {
    const [cuerpo, comentario] = ln.split(/\s+#/);
    runs.push({ text: cuerpo.replace(/\s+$/, "") + (comentario !== undefined ? "  " : ""),
      options: { color: C.navy, fontFace: FUENTE_CODIGO, fontSize: tam } });
    if (comentario !== undefined) runs.push({ text: "# " + comentario,
      options: { color: C.teal, fontFace: FUENTE_CODIGO, fontSize: tam } });
    runs[runs.length - 1].options.breakLine = i < lineas.length - 1;
  });
  tarjeta(s, x, y, w, h, C.code);
  s.addText(runs, { x: x + 0.2, y: y + 0.12, w: w - 0.4, h: h - 0.24, valign: "top", margin: 0, paraSpaceAfter: 0,
    lineSpacingMultiple: 1.15 });
}
function celda(t, o = {}) { return { text: t, options: o }; }
const cab = (t) => celda(t, { bold: true, color: C.white, fill: { color: C.navy } });

// ================= 1. Portada =================
{
  const s = pres.addSlide({ masterName: "PORTADA", sectionTitle: declarar("Presentación") });
  s.addText("Flujo laminar sobre un escalón descendente", { placeholder: "title" });
  texto(s, "PROYECTO FINAL · MECÁNICA DE FLUIDOS", 0.6, 1.2, 6.4, 0.4, { fontSize: 13, bold: true, color: C.aqua });
  texto(s, "Navier–Stokes 2D con el método de proyección: formulación, discretización, código y validación",
    0.6, 3.85, 6.0, 0.9, { fontSize: 17, color: "C9D6E3" });
  texto(s, "Luis Antonio Pérez Hernández\nMarco Antonio Navarrete Baños", 0.6, 5.2, 6.0, 0.8,
    { fontSize: 16, color: C.white, paraSpaceAfter: 4 });
  texto(s, "Prof. Anuar Sánchez", 0.6, 6.3, 6.0, 0.4, { fontSize: 13, color: "9FB0C4" });
  imagen(s, path.join(EQ, "arranque_re200_portada.png"), 7.1, 2.0, 5.6, 3.6, false);
  s.addNotes("AMBOS (0:30). LUIS: presentarse; simulación del flujo laminar sobre un escalón descendente con código propio en Python. MARCO: orden de la exposición: física y ecuaciones → método → código funcionando → cómo sabemos que es correcto.");
}

// ================= 2. Fenómeno y caso base =================
{
  const s = nueva("El fenómeno y el caso base: Re = 200", { seccion: "Problema físico" });
  const pasos = [
    ["La capa límite se separa", "En la arista, el fluido pegado a la pared no puede seguir el cambio de geometría."],
    ["Aparece un remolino", "Bajo la capa de corte, la velocidad es negativa: u < 0."],
    ["La presión sube", "Al ensancharse el canal, ∂p/∂x > 0: gradiente adverso."],
    ["El flujo vuelve a pegarse", "En el reacoplamiento, τ_w = 0 y x_r/S = 4.91."],
  ];
  pasos.forEach(([t, d], i) => {
    const y = 1.5 + i * 1.2;
    circulo(s, i + 1, 0.6, y + 0.04);
    texto(s, t, 1.3, y, 3.9, 0.35, { fontSize: 16, bold: true, color: C.navy });
    texto(s, d, 1.3, y + 0.36, 3.9, 0.7, { fontSize: 13, color: C.grey });
  });
  tarjeta(s, 0.6, 6.25, 4.6, 0.55, C.paper);
  texto(s, "2 608 pasos · ~3 s de cálculo · |∇·u|máx ≈ 6·10⁻¹⁵", 0.8, 6.36, 4.3, 0.35, { fontSize: 12, color: C.navy, bold: true });
  imagen(s, path.join(FIG, "campos_base.png"), 5.5, 1.5, 7.3, 5.2);
  s.addNotes("LUIS (1:15). Canal que se ensancha al doble → el fluido se frena → la presión sube (gradiente adverso, ∂p/∂x > 0) → el fluido lento junto a la pared se separa en la esquina. Remolino con u < 0; reacoplamiento donde τ_w = 0. Señalar la presión subiendo en la figura de abajo. Caso base Re = 200: x_r/S = 4.91. MARCO pregunta por qué es caso de prueba → geometría simple, todos los mecanismos, datos de Armaly (1983).");
}

// ================= 3. Ecuaciones de gobierno =================
{
  const s = nueva("Ecuaciones de gobierno", { seccion: "Formulación" });
  tarjeta(s, 0.6, 1.45, 8.1, 5.35);
  texto(s, "Continuidad (conservación de la masa)", 0.9, 1.7, 7.5, 0.3, { fontSize: 13, bold: true, color: C.teal });
  eq(s, "continuidad", 0.9, 2.05, 7.5, 0.6);
  texto(s, "Cantidad de movimiento (Navier–Stokes), forma conservativa", 0.9, 3.0, 7.5, 0.3, { fontSize: 13, bold: true, color: C.teal });
  eq(s, "mom_x", 0.9, 3.4, 7.5, 0.8);
  eq(s, "mom_y", 0.9, 4.45, 7.5, 0.8);
  texto(s, "La forma conservativa (∂(u²)/∂x en lugar de u ∂u/∂x) es equivalente por continuidad, y es la que discretizamos: "
    + "el momento que sale de una celda es el que entra a la vecina.", 0.9, 5.45, 7.5, 1.2, { fontSize: 12, color: C.grey });

  tarjeta(s, 9.0, 1.45, 3.7, 5.35, C.paper);
  texto(s, "Adimensionalización", 9.25, 1.7, 3.3, 0.3, { fontSize: 13, bold: true, color: C.teal });
  eq(s, "adim", 9.25, 2.05, 3.3, 0.9);
  texto(s, "Geometría", 9.25, 3.2, 3.3, 0.3, { fontSize: 13, bold: true, color: C.teal });
  eq(s, "geom", 9.25, 3.55, 3.3, 0.45);
  texto(s, "Supuestos", 9.25, 4.25, 3.3, 0.3, { fontSize: 13, bold: true, color: C.teal });
  lista(s, ["2D, incompresible, newtoniano", "Isotérmico y laminar (Re ≤ 600)", "Sin gravedad: sólo añade presión hidrostática",
    "Un único parámetro: Re = UH/ν"], 9.25, 4.6, 3.3, 2.1, 12);
  s.addNotes("LUIS (1:45). Continuidad: ∇·u = 0. Navier–Stokes adimensional con H, U, ρU² → un solo parámetro Re = UH/ν; ν = 1/Re: variar la viscosidad = variar Re. Forma conservativa: (u·∇)u = ∇·(uu) − u(∇·u), el último término es cero; el momento que sale de una celda entra a la vecina. Supuestos: 2D, newtoniano, isotérmico, laminar (Re ≤ 600, transición ~1200), sin gravedad. MARCO: ¿la presión no tiene ecuación? → es la que hace cumplir continuidad.");
}

// ================= 4. Condiciones iniciales y de frontera =================
{
  const s = nueva("Condiciones iniciales y de frontera", { seccion: "Formulación" });
  const bloques = [
    ["Condición inicial, t = 0", "ci", "Fluido en reposo en todo el dominio."],
    ["Entrada, x = −2H", "entrada", "Perfil de Poiseuille: velocidad media U, máxima 1.5U."],
    ["No deslizamiento", "noslip", "Piso, techo, tapa y cara del escalón."],
    ["Salida, x = L", "salida", "Flujo ya desarrollado; referencia de presión."],
    ["Presión en paredes y entrada", "neumann", "Sale de evaluar la cantidad de movimiento donde u = 0."],
    ["Referencia de presión", "poisson", "Con p = 0 en la salida, la matriz de Poisson no es singular."],
  ];
  bloques.forEach(([titulo, nombre, nota], i) => {
    const col = i % 2, fila = Math.floor(i / 2);
    const x = 0.6 + col * 6.15, y = 1.45 + fila * 1.8;
    tarjeta(s, x, y, 5.95, 1.6, C.paper);
    texto(s, titulo, x + 0.3, y + 0.15, 5.4, 0.3, { fontSize: 13, bold: true, color: C.teal });
    if (nombre === "poisson") {
      eq(s, "fantasma", x + 0.3, y + 0.55, 5.4, 0.5);
      texto(s, nota, x + 0.3, y + 1.1, 5.4, 0.4, { fontSize: 11, color: C.grey });
    } else {
      eq(s, nombre, x + 0.3, y + 0.5, 5.4, 0.6);
      texto(s, nota, x + 0.3, y + 1.15, 5.4, 0.4, { fontSize: 11, color: C.grey });
    }
  });
  s.addNotes("LUIS (1:30). CI: reposo, se avanza hasta el estado estacionario. Entrada x = −2H: Poiseuille 6Uη(1−η); el 6 da media U, máxima 1.5U. No deslizamiento en piso, techo y escalón. Salida: flujo desarrollado y p = 0 (canal hasta 25H). Presión: Neumann en paredes; p = 0 en la salida da solución única. Pasar la palabra: «Marco, ¿cómo lo resolvemos?»");
}

// ================= 5. Método de proyección =================
{
  const s = nueva("Método de proyección de Chorin (1968)", { seccion: "Método numérico" });
  const tarjetas = [
    ["Velocidad de prueba", ["paso1", "def_A"], "Navier–Stokes sin presión. Adams–Bashforth (2.º orden) estima A a mitad de paso."],
    ["Presión", ["paso2"], "La presión que hace cumplir continuidad. Se obtiene de la divergencia del paso 3."],
    ["Corrección", ["paso3"], "La velocidad se corrige con el gradiente de presión: el resultado es solenoidal."],
  ];
  tarjetas.forEach(([t, eqs, d], i) => {
    const x = 0.6 + i * 4.1;
    tarjeta(s, x, 1.45, 3.85, 3.2);
    circulo(s, i + 1, x + 0.3, 1.65);
    texto(s, t, x + 0.9, 1.7, 2.8, 0.4, { fontSize: 16, bold: true, color: C.navy });
    let y = 2.35;
    eqs.forEach((e) => { y += eq(s, e, x + 0.3, y, 3.3, 0.6) + 0.15; });
    texto(s, d, x + 0.3, 3.75, 3.3, 0.85, { fontSize: 12, color: C.grey });
  });
  tarjeta(s, 0.6, 4.9, 12.1, 1.85, C.navy);
  texto(s, "Por qué funciona: se aplica la divergencia al paso 3 y se exige ∇·uⁿ⁺¹ = 0", 0.95, 5.05, 11.5, 0.35,
    { fontSize: 14, bold: true, color: C.aqua });
  tarjeta(s, 0.95, 5.42, 11.5, 0.78, C.white);
  eq(s, "deriv", 1.15, 5.47, 11.1, 0.68);
  texto(s, "Sumando los pasos 1 y 3 se recupera la ecuación de cantidad de movimiento discretizada en el tiempo. "
    + "La presión no tiene ecuación propia: es el multiplicador que impone la continuidad.", 0.95, 6.25, 11.5, 0.5,
    { fontSize: 12, color: "C9D6E3" });
  s.addNotes("MARCO (1:45). Tres incógnitas y la presión sin ecuación de evolución. Paso 1: u* sin presión, Adams–Bashforth (3/2 Aⁿ − 1/2 Aⁿ⁻¹). Paso 2: pedir ∇·uⁿ⁺¹ = 0 en uⁿ⁺¹ = u* − Δt∇p → Poisson ∇²p = ∇·u*/Δt. Paso 3: corregir. Pasos 1 + 3 = Navier–Stokes discretizada. LUIS: ¿por qué no Euler? → explota a los 706 pasos; AB2 cuesta lo mismo.");
}

// ================= 6. Discretización espacial =================
{
  const s = nueva("Discretización espacial: malla escalonada (MAC)", { seccion: "Método numérico" });
  imagen(s, path.join(FIG, "malla_escalonada.png"), 0.6, 1.45, 5.0, 3.6, false);
  texto(s, "p en el centro de cada celda; u en las caras verticales; v en las horizontales. El gradiente de presión "
    + "usa dos nodos vecinos directos y se evita el desacople presión–velocidad.", 0.6, 5.2, 5.0, 1.5, { fontSize: 12, color: C.grey });
  const filas = [
    ["Difusión (5 puntos)", "lap", "Error de truncamiento O(Δx²)."],
    ["Convección, forma conservativa", "conv", "Valor en la cara: promedio de los dos nodos."],
    ["Gradiente de presión", "grad", "Diferencia entre celdas vecinas."],
    ["Poisson para p", "poisson", "Una ecuación por celda; A es dispersa."],
  ];
  filas.forEach(([t, nombre, nota], i) => {
    const y = 1.45 + i * 1.3;
    tarjeta(s, 6.1, y, 6.6, 1.15, C.paper);
    texto(s, t, 6.35, y + 0.1, 6.1, 0.3, { fontSize: 13, bold: true, color: C.teal });
    eq(s, nombre, 6.35, y + 0.42, 6.1, 0.4);
    texto(s, nota, 6.35, y + 0.82, 6.1, 0.3, { fontSize: 11, color: C.grey });
  });
  texto(s, "Orden formal de la discretización: segundo orden en Δx. Comprobado en el estudio de malla (diapositiva 9).",
    6.1, 6.7, 6.6, 0.3, { fontSize: 11, color: C.navy, bold: true });
  s.addNotes("MARCO (1:45). Celdas cuadradas; malla escalonada: p en el centro, u y v en las caras → cada velocidad entre dos presiones, sin tablero de ajedrez. Difusión: 5 puntos. Convección conservativa con promedio en las caras: segundo orden (upwind acortaría la burbuja). Poisson: vecino pared no se suma (Neumann); salida a media celda → −2. Escalón = celdas sólidas.");
}

// ================= 7. Código I =================
{
  const s = nueva("Código I: matriz de Poisson y condiciones de frontera", { seccion: "Código" });
  codigo(s, [
    "A = sps.lil_matrix((NX * NY, NX * NY))   # una ecuación por celda",
    "for i in range(NX):                      # columnas de celdas (x)",
    "    for j in range(NY):                  # filas de celdas (y)",
    "        k = i * NY + j                   # número de la celda (i, j)",
    "        if solido[i, j]:                 # escalón: p = 0, ecuación trivial",
    "            A[k, k] = 1; continue",
    "        for vi, vj in [(i+1, j), (i-1, j), (i, j+1), (i, j-1)]:",
    "            if vi == NX:                 # salida: p fantasma = -p",
    "                A[k, k] -= 2",
    "            elif vi >= 0 and 0 <= vj < NY and not solido[vi, vj]:",
    "                A[k, vi*NY + vj] = 1; A[k, k] -= 1   # vecino con fluido",
    "return spla.splu(A.tocsc() / dx**2, permc_spec=\"MMD_AT_PLUS_A\")  # LU",
  ], 0.6, 1.45, 7.4, 3.7, 11);
  codigo(s, [
    "v[0, :] = -v[1, :]                  # entrada: v = 0 (espejo)",
    "u[:I0+1, 1:J0+1] = 0.0              # escalón: u = 0",
    "u[:, 0] = -u[:, 1]                  # piso: u = 0 (espejo)",
    "u[:, -1] = -u[:, -2]                # techo: u = 0",
    "v[-1, :] = v[-2, :]                 # salida: ∂v/∂x = 0",
  ], 0.6, 5.35, 7.4, 1.5, 11);
  texto(s, "Lectura del código", 8.4, 1.45, 4.3, 0.35, { fontSize: 16, bold: true, color: C.navy });
  lista(s, [
    "Cada fila de A es la ecuación de una celda: suma de las diferencias con sus vecinos, igual a b·Δx².",
    "Vecino sin fluido o pared: dp/dn = 0, ese término no se suma (Neumann).",
    "En la salida, la cara está a Δx/2 y p = 0: el término vale −2p_P, como en la ecuación de referencia.",
    "La matriz no depende de Δt ni del tiempo: LU se calcula una sola vez y cada paso sólo resuelve.",
    "En la fila 'fantasma' el espejo impone la condición: el promedio en la pared da el valor deseado.",
  ], 8.4, 1.9, 4.3, 5.0, 12);
  s.addNotes("MARCO (1:15). Código real del notebook. k = i·NY + j; cada fila es la ecuación de una celda; sólida → trivial; salida → −2; vecino con fluido → +1 / −1. La matriz no cambia en el tiempo → LU una sola vez. Fronteras con celdas fantasma: fantasma = −nodo → promedio cero en la pared. LUIS: el no deslizamiento queda a media celda.");
}

// ================= 8. Código II =================
{
  const s = nueva("Código II: el ciclo de tres pasos y el criterio de convergencia", { seccion: "Código" });
  codigo(s, [
    "Au, Av = aceleracion_u(u, v, nu, dx), aceleracion_v(u, v, nu, dx)",
    "u_est[1:-1, 1:-1] += dt * (1.5 * Au - 0.5 * Au_ant)   # paso 1: AB2",
    "div = (u_est[1:, 1:-1] - u_est[:-1, 1:-1]",
    "       + v_est[1:-1, 1:] - v_est[1:-1, :-1]) / dx        # ∇·u*",
    "p = resolver_p.solve((div / dt).ravel()).reshape(NX, NY)  # paso 2: Poisson",
    "u[1:-1, 1:-1] -= dt * (p[1:, :] - p[:-1, :]) / dx          # paso 3: ∂p/∂x",
    "v[1:-1, 1:-1] -= dt * (p[:, 1:] - p[:, :-1]) / dx          # paso 3: ∂p/∂y",
    "cambio = np.max(np.abs(u - u_viejo)) / dt                   # residuo",
    "if cambio < tol and t > 5: break                            # convergencia",
  ], 0.6, 1.45, 7.4, 3.95, 11);
  eq(s, "criterio", 0.6, 5.6, 7.4, 0.55);
  texto(s, "tol = 10⁻⁴ en las unidades adimensionales. Con 10⁻⁵ el valor de x_r cambia menos de 0.3 %.",
    0.6, 6.3, 7.4, 0.5, { fontSize: 12, color: C.grey });
  texto(s, "Correspondencia con el método", 8.4, 1.45, 4.3, 0.35, { fontSize: 16, bold: true, color: C.navy });
  const pasos = [
    ["paso1", "Velocidad de prueba: aceleración a mitad de paso con AB2."],
    ["paso2", "Poisson: la divergencia de u* alimenta el vector b."],
    ["paso3", "Corrección: los gradientes de p se restan en cada cara."],
  ];
  pasos.forEach(([e, t], i) => {
    const y = 1.95 + i * 1.5;
    tarjeta(s, 8.4, y, 4.3, 1.3, C.paper);
    eq(s, e, 8.6, y + 0.12, 3.9, 0.45);
    texto(s, t, 8.6, y + 0.7, 3.9, 0.55, { fontSize: 12, color: C.grey });
  });
  texto(s, "Cada iteración es un Δt. Los pasos 1 a 3 ocurren en ese orden, y la masa se verifica al final del ciclo.",
    8.4, 6.45, 4.3, 0.5, { fontSize: 11, color: C.navy, bold: true });
  s.addNotes("MARCO (1:00). Cada línea es una ecuación: aceleración, paso 1 con AB2, divergencia de u*, paso 2 (Poisson), paso 3 (diferencias de p en las caras). Residuo < 1e-4 → estado estacionario. «Ahora lo vemos correr.» → DEMO (2:30): RE = 400 (8.26, ~8 s, burbuja del techo 4.2–4.5); simular(200, dt=(H/20)/1.5, t_max=150) explota en 36 pasos; simular(200, ab2=False, t_max=150) explota en 706. Regresar RE = 200.");
}

// ================= 9. Estabilidad y convergencia =================
{
  const s = nueva("Estabilidad y convergencia", { seccion: "Estabilidad y convergencia" });
  tarjeta(s, 0.6, 1.45, 6.0, 5.35, C.paper);
  texto(s, "Estabilidad: límites de Δt (Euler y AB2)", 0.9, 1.65, 5.5, 0.3, { fontSize: 13, bold: true, color: C.teal });
  eq(s, "cfl", 0.9, 2.05, 5.4, 0.6);
  texto(s, "Δx = 0.05, u_max = 1.5 → Δt_CFL = 0.033", 0.9, 2.75, 5.4, 0.3, { fontSize: 12, color: C.ink });
  eq(s, "difusion", 0.9, 3.15, 5.4, 0.55);
  texto(s, "Re = 200 → Δt_difusión = 0.125. Manda el CFL. Usamos CFL = 0.5.", 0.9, 3.85, 5.4, 0.3, { fontSize: 12, color: C.ink });
  texto(s, "Convergencia al estado estacionario", 0.9, 4.35, 5.5, 0.3, { fontSize: 13, bold: true, color: C.teal });
  eq(s, "criterio", 0.9, 4.75, 5.4, 0.55);
  lista(s, ["Dentro del CFL el resultado no cambia: sólo cambia el número de pasos.",
    "Euler simple diverge en 706 pasos, aun con Δt = 0.5 Δt_CFL.",
    "Por encima del CFL la solución explota en 36 pasos."], 0.9, 5.45, 5.4, 1.3, 12);

  s.addChart(pres.charts.BAR, [{ name: "x_r/S", labels: ["10 celdas/H", "20 celdas/H", "40 celdas/H"],
    values: [4.754, 4.914, 4.946] }], {
    x: 6.9, y: 1.45, w: 5.8, h: 2.9, barDir: "col", chartColors: [C.teal], barGapWidthPct: 70,
    showTitle: true, title: "Estudio de malla, x_r/S (Re = 200)", titleFontFace: FUENTE_TEXTO, titleFontSize: 13,
    titleColor: C.navy, showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 12, dataLabelColor: C.ink,
    dataLabelFormatCode: "0.000", valAxisMinVal: 4.7, valAxisMaxVal: 5.0, valAxisMajorUnit: 0.1,
    valAxisLabelFormatCode: "0.0", catAxisLabelFontSize: 11, valAxisLabelFontSize: 10,
    catAxisLabelColor: C.ink, valAxisLabelColor: C.grey, valGridLine: { color: C.line, size: 0.5 },
    catGridLine: { style: "none" }, showLegend: false, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    dataLabelFontFace: "+mn-lt",
  });
  eq(s, "orden", 6.9, 4.5, 5.8, 0.5);
  texto(s, "Orden observado p ≈ 2.3 (formal 2). Extrapolado: x_r/S ≈ 4.95, así que el error con 20 celdas es ≈ 0.8 %.",
    6.9, 5.05, 5.8, 0.5, { fontSize: 12, color: C.ink });
  const cab2 = (t) => celda(t, { bold: true, color: C.white, fill: { color: C.navy } });
  s.addTable([
    [cab2("Δt / Δt_CFL"), cab2("Resultado"), cab2("x_r/S")],
    ["0.25", "converge", "4.914"], ["0.50", "converge", "4.914"], ["0.80", "converge", "4.914"],
    ["1.00", "diverge en 36 pasos", "—"], ["Euler, 0.50", "diverge en 706 pasos", "—"],
  ], { x: 6.9, y: 5.55, w: 5.8, colW: [1.7, 2.7, 1.4], fontFace: FUENTE_TEXTO, fontSize: 11, color: C.ink,
    rowH: 0.22, border: { type: "solid", pt: 0.5, color: C.line }, margin: [0.02, 0.08, 0.02, 0.08], valign: "middle" });
  s.addNotes("LUIS (1:30). CFL: Δt ≤ Δx/|u|max = 0.05/1.5 = 0.033; difusivo 0.125 → manda CFL; usamos la mitad. 0.25/0.5/0.8 → 4.914 idéntico; 1.0 explota (lo vimos). Malla 10/20/40 → 4.754/4.914/4.946; orden observado log2(0.160/0.032) ≈ 2.3; Richardson 4.95 → error 0.8 % con 20 celdas. MARCO: ¿y la masa? → divergencia ~1e-15.");
}

// ================= 10. Análisis paramétrico: viscosidad =================
{
  const s = nueva("Análisis paramétrico: viscosidad (Re)", { seccion: "Resultados" });
  video(s, path.join(FIG, "comparacion_re.mp4"), path.join(EQ, "comparacion_re_portada.png"), 0.6, 1.45, 7.4);
  texto(s, "Re = 100, 300 y 600 con NY = 20 y L = 25H. Abajo, x_r(t) y u junto al piso.",
    0.6, 5.75, 7.4, 0.4, { fontSize: 12, color: C.grey });
  const cab3 = (t) => celda(t, { bold: true, color: C.white, fill: { color: C.navy } });
  s.addTable([
    [cab3("Re"), cab3("ν"), cab3("x_r/S"), cab3("Burbuja del techo, x/H")],
    ["100", "0.0100", "2.84", "—"], ["200", "0.0050", "4.91", "—"], ["300", "0.0033", "6.73", "—"],
    ["400", "0.0025", "8.26", "4.20 – 4.50"], ["500", "0.0020", "9.40", "4.00 – 6.30"], ["600", "0.0017", "10.06", "4.05 – 7.60"],
  ], { x: 8.3, y: 1.45, w: 4.4, colW: [0.7, 0.9, 0.9, 1.9], fontFace: FUENTE_TEXTO, fontSize: 12, color: C.ink,
    rowH: 0.38, border: { type: "solid", pt: 0.5, color: C.line }, margin: [0.03, 0.07, 0.03, 0.07], valign: "middle", align: "center" });
  tarjeta(s, 8.3, 4.5, 4.4, 1.2, C.paper);
  texto(s, "Reacoplamiento", 8.5, 4.6, 4.0, 0.3, { fontSize: 13, bold: true, color: C.teal });
  eq(s, "tauw", 8.5, 4.95, 4.1, 0.45);
  texto(s, "Mayor Re → menor ν → burbuja más larga, casi lineal hasta Re ≈ 400.", 8.3, 5.9, 4.4, 0.6,
    { fontSize: 12, color: C.grey });
  s.addNotes("MARCO (1:30). Reproducir el video: Re 100, 300, 600 desde el reposo; tinta = partículas arrastradas. x_r/S de 2.84 a 10.06: menos viscosidad → la difusión transmite el momento al piso más lento. Casi lineal hasta 400; después la burbuja del techo empuja el chorro hacia abajo. LUIS: el tiempo al estacionario crece de 20 a 289.");
}

// ================= 11. Validación =================
{
  const s = nueva("Validación con la literatura", { seccion: "Validación" });
  const re = ["100", "200", "300", "400", "500", "600"];
  s.addChart(pres.charts.LINE, [
    { name: "Literatura (2D)", labels: re, values: [3.00, 4.95, 6.75, 8.10, 9.30, 10.05] },
    { name: "Este trabajo", labels: re, values: [2.84, 4.91, 6.73, 8.26, 9.40, 10.06] },
  ], {
    x: 0.6, y: 1.45, w: 7.2, h: 5.2, chartColors: [C.grey, C.coral], lineSize: 2.5, lineDataSymbol: "circle",
    lineDataSymbolSize: 9, lineDataSymbolLineColor: C.white,
    showTitle: true, title: "Longitud de reacoplamiento x_r/S contra Re", titleFontFace: FUENTE_TEXTO,
    titleFontSize: 14, titleColor: C.navy, showLegend: true, legendPos: "b", legendFontSize: 12, legendColor: C.ink,
    catAxisTitle: "Re", showCatAxisTitle: true, catAxisTitleFontSize: 12, catAxisTitleColor: C.grey,
    valAxisTitle: "x_r / S", showValAxisTitle: true, valAxisTitleFontSize: 12, valAxisTitleColor: C.grey,
    valAxisMinVal: 2, valAxisMaxVal: 11, valAxisMajorUnit: 1, valAxisLabelFormatCode: "0",
    catAxisLabelFontSize: 12, valAxisLabelFontSize: 11, catAxisLabelColor: C.ink, valAxisLabelColor: C.grey,
    valGridLine: { color: C.line, size: 0.5 }, catGridLine: { style: "none" },
    catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", legendFontFace: "+mn-lt",
  });
  const filas = [
    [cab("Re"), cab("Este trabajo"), cab("Literatura"), cab("Dif.")],
    ["100", "2.84", "3.00", "−5.4 %"], ["200", "4.91", "4.95", "−0.7 %"], ["300", "6.73", "6.75", "−0.3 %"],
    ["400", "8.26", "8.10", "+2.0 %"], ["500", "9.40", "9.30", "+1.1 %"], ["600", "10.06", "10.05", "+0.1 %"],
  ];
  s.addTable(filas, { x: 8.2, y: 1.6, w: 4.5, colW: [0.8, 1.35, 1.25, 1.1], fontFace: FUENTE_TEXTO, fontSize: 13,
    color: C.ink, rowH: 0.4, border: { type: "solid", pt: 0.5, color: C.line }, margin: [0.03, 0.07, 0.03, 0.07],
    valign: "middle", align: "center" });
  texto(s, "Para 200 ≤ Re ≤ 600 la diferencia es de 2 % o menos. El error de malla es < 1 %, así que la diferencia "
    + "es del orden de la dispersión entre estudios publicados.", 8.2, 4.7, 4.5, 1.4, { fontSize: 12, color: C.grey });
  texto(s, "Referencia de la tabla: arXiv:2507.16509 (Tabla 1). Concuerda con Armaly et al. (1983) hasta Re ≈ 400.",
    8.2, 6.2, 4.5, 0.6, { fontSize: 10, color: "8A96A6" });
  s.addNotes("LUIS (1:00). Simulaciones 2D publicadas: ≤ 2 % entre Re 200 y 600; 5 % en Re 100. Error de malla < 1 % → la diferencia es del orden de la dispersión entre estudios (canal de entrada, dominio). Remolino del techo desde Re ≈ 400, como la literatura.");
}

// ================= 12. Conclusiones =================
{
  const s = nueva("Conclusiones", { oscura: true, seccion: "Conclusiones" });
  const items = [
    ["Formulación", "Continuidad y Navier–Stokes con condiciones de frontera explícitas; masa conservada a precisión de máquina."],
    ["Método", "Proyección de Chorin con Adams–Bashforth (2.º orden), malla MAC y Poisson con factorización LU."],
    ["Estabilidad y convergencia", "CFL = 0.5 garantiza estabilidad; error de malla < 1 % con 20 celdas/H (orden observado 2.3)."],
    ["Resultados", "Remolino y reacoplamiento reproducidos; remolino del techo desde Re ≈ 400; 2 % o menos frente a la literatura."],
  ];
  items.forEach(([t, d], i) => {
    const x = 0.6 + (i % 2) * 6.15, y = 1.45 + Math.floor(i / 2) * 2.4;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 5.95, h: 2.15, rectRadius: 0.1,
      fill: { color: C.navy2 }, line: { type: "none" } });
    texto(s, String(i + 1).padStart(2, "0"), x + 0.3, y + 0.25, 1.0, 0.6,
      { fontFace: FUENTE_TITULO, fontSize: 28, bold: true, color: C.aqua });
    texto(s, t, x + 1.35, y + 0.3, 4.4, 0.45, { fontSize: 17, bold: true, color: C.white });
    texto(s, d, x + 1.35, y + 0.8, 4.4, 1.2, { fontSize: 13, color: "C9D6E3" });
  });
  texto(s, "Código: escalon_descendente.ipynb · Ejecutar todo (~5 min con videos, ~3 min sin ellos)", 0.6, 6.4, 12.1, 0.35,
    { fontSize: 12, color: "9FB0C4", align: "center" });
  texto(s, "¡Gracias! Preguntas", 0.6, 6.75, 12.1, 0.45, { fontFace: FUENTE_TITULO, fontSize: 20, bold: true,
    color: C.white, align: "center" });
  s.addNotes("AMBOS (0:45). LUIS: formulación y verificación: estable dentro del CFL, segundo orden, error de malla < 1 %. MARCO: proyección en malla escalonada, masa conservada, física reproducida, ≤ 2 % frente a la literatura. Gracias; preguntas.");
}

pres.writeFile({ fileName: path.join(AQUI, "presentacion.pptx") }).then((f) => console.log("escrito", f));
