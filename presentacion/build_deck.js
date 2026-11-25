// Genera presentacion.pptx (12 diapositivas) con pptxgenjs.
// Uso (desde presentacion/):  npm install  →  python render_eqs.py  →  node build_deck.js  →  python transiciones.py presentacion.pptx
// Requiere que el notebook ya haya generado ../figures/*.png y los videos ../figures/*.mp4.
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const AQUI = __dirname;
const FIG = path.join(AQUI, "..", "figures");
const EQ = path.join(AQUI, "eq");

// Paleta: azul-marino de la pared del canal, verde-azulado del flujo y coral para el punto de reacoplamiento.
const C = {
  navy: "0B1F3A", navy2: "1A3457", teal: "0E7C86", aqua: "7FD1D6", coral: "F26B3A",
  ink: "1E2A38", grey: "5B6878", paper: "F4F7FA", white: "FFFFFF", line: "D5DEE8",
};
const FUENTE_TITULO = "Cambria";
const FUENTE_TEXTO = "Calibri";

function tamanoPNG(archivo) {
  const b = fs.readFileSync(archivo);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}
// Ajusta una imagen dentro de una caja (sin deformarla) y devuelve sus dimensiones finales.
function encajar(archivo, x, y, maxW, maxH) {
  const { w, h } = tamanoPNG(archivo);
  const k = Math.min(maxW / w, maxH / h);
  return { x: x + (maxW - w * k) / 2, y: y + (maxH - h * k) / 2, w: w * k, h: h * k };
}
const sombra = () => ({ type: "outer", blur: 10, offset: 3, angle: 90, color: "000000", opacity: 0.18 });

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";                       // 13.33 × 7.5 in
pres.author = "Luis Antonio Pérez Hernández · Marco Antonio Navarrete Baños";
pres.title = "Flujo laminar sobre un escalón descendente";
pres.theme = { headFontFace: FUENTE_TITULO, bodyFontFace: FUENTE_TEXTO };

// ---------- plantillas ----------
pres.defineSlideMaster({
  title: "CONTENIDO",
  background: { color: C.white },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.1, h: 0.9, valign: "middle",
      fontFace: FUENTE_TITULO, fontSize: 32, bold: true, color: C.navy, align: "left", margin: 0 }, text: "" } },
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
      fontFace: FUENTE_TITULO, fontSize: 32, bold: true, color: C.white, align: "left", margin: 0 }, text: "" } },
  ],
});

// Transiciones: el archivo se marca después con transiciones.py (fundido en todas las diapositivas).
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
function circulo(s, n, x, y, d = 0.5, color = C.teal) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color }, line: { type: "none" } });
  s.addText(String(n), { x, y, w: d, h: d, align: "center", valign: "middle", fontFace: FUENTE_TEXTO,
    fontSize: Math.round(d * 30), bold: true, color: C.white, margin: 0 });
}
function tarjeta(s, x, y, w, h, color = C.paper) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color },
    line: { type: "none" }, shadow: color === C.paper ? undefined : sombra() });
}
function imagen(s, archivo, x, y, maxW, maxH, conTarjeta = true) {
  const p = encajar(archivo, x, y, maxW, maxH);
  if (conTarjeta) tarjeta(s, p.x - 0.1, p.y - 0.1, p.w + 0.2, p.h + 0.2, C.white);
  s.addImage({ path: archivo, x: p.x, y: p.y, w: p.w, h: p.h });
  return p;
}
function video(s, archivo, poster, x, y, w) {
  const h = w * 9 / 16;
  const cover = "data:image/png;base64," + fs.readFileSync(poster).toString("base64");
  s.addMedia({ type: "video", path: archivo, x, y, w, h, cover });
  return h;
}
function lista(s, items, x, y, w, h, tam = 15) {
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })),
    { x, y, w, h, fontFace: FUENTE_TEXTO, fontSize: tam, color: C.ink, valign: "top", paraSpaceAfter: 8, margin: 0 });
}
function texto(s, t, x, y, w, h, o = {}) {
  s.addText(t, Object.assign({ x, y, w, h, fontFace: FUENTE_TEXTO, fontSize: 15, color: C.ink, valign: "top", margin: 0 }, o));
}
const EQ_W = (f) => tamanoPNG(path.join(EQ, f + ".png"));
function ecuacion(s, nombre, x, y, anchoMax, altoMax) {
  const { w, h } = EQ_W(nombre);
  const k = Math.min(anchoMax / w, altoMax / h);
  s.addImage({ path: path.join(EQ, nombre + ".png"), x, y, w: w * k, h: h * k });
  return h * k;
}

// ================= 1. Portada =================
{
  const s = pres.addSlide({ masterName: "PORTADA", sectionTitle: declarar("Presentación") });
  s.addText("Flujo laminar sobre un escalón descendente", { placeholder: "title" });
  texto(s, "PROYECTO FINAL · MECÁNICA DE FLUIDOS", 0.6, 1.2, 6.4, 0.4, { fontSize: 13, bold: true, color: C.aqua });
  texto(s, "Navier–Stokes 2D con el método de proyección: análisis paramétrico y validación", 0.6, 3.85, 6.0, 0.9,
    { fontSize: 18, color: "C9D6E3" });
  texto(s, "Luis Antonio Pérez Hernández\nMarco Antonio Navarrete Baños", 0.6, 5.2, 6.0, 0.8,
    { fontSize: 16, color: C.white, paraSpaceAfter: 4 });
  texto(s, "Prof. Anuar Sánchez", 0.6, 6.3, 6.0, 0.4, { fontSize: 13, color: "9FB0C4" });
  video(s, path.join(FIG, "arranque_re200.mp4"), path.join(EQ, "arranque_re200_portada.png"), 7.1, 2.0, 5.6);
  s.addNotes("Presentación del equipo (30 s). El video de la derecha es la simulación del arranque; "
    + "la presentación técnica empieza en la diapositiva 2.");
}

// ================= 2. Fenómeno =================
{
  const s = nueva("¿Qué pasa en un escalón descendente?", { seccion: "El problema" });
  const pasos = [
    ["La capa límite se separa", "El fluido pegado a la pared no tiene inercia para seguir el cambio de geometría."],
    ["Aparece un remolino", "Bajo la capa de corte la velocidad es negativa (u < 0)."],
    ["La presión sube", "El fluido se frena al ensancharse el canal: gradiente adverso."],
    ["El flujo vuelve a pegarse", "En el reacoplamiento x_r la tensión en la pared es cero."],
  ];
  pasos.forEach(([t, d], i) => {
    const y = 1.55 + i * 1.3;
    circulo(s, i + 1, 0.6, y + 0.05, 0.52);
    texto(s, t, 1.35, y, 4.0, 0.4, { fontSize: 17, bold: true, color: C.navy });
    texto(s, d, 1.35, y + 0.4, 4.0, 0.7, { fontSize: 14, color: C.grey });
  });
  imagen(s, path.join(FIG, "campos_base.png"), 5.6, 1.45, 7.2, 5.2);
  s.addNotes("Explicar separación por gradiente de presión adverso, capa de corte, burbuja de recirculación, "
    + "reacoplamiento (τ_pared = 0) y, para Re > 400, la burbuja secundaria en el techo.");
}

// ================= 3. Modelo =================
{
  const s = nueva("Modelo físico: ecuaciones y supuestos", { seccion: "Modelo y método" });
  tarjeta(s, 0.6, 1.5, 7.3, 5.2);
  texto(s, "Ecuaciones de gobierno (adimensionales)", 0.95, 1.75, 6.6, 0.4, { fontSize: 15, bold: true, color: C.teal });
  let y = 2.35;
  y += ecuacion(s, "continuidad", 0.95, y, 6.6, 0.7) + 0.45;
  y += ecuacion(s, "momento", 0.95, y, 6.6, 1.1) + 0.45;
  ecuacion(s, "adimensional", 0.95, y, 6.6, 0.7);
  texto(s, "Poiseuille en la entrada:", 0.95, 5.55, 6.6, 0.35, { fontSize: 13, color: C.grey });
  ecuacion(s, "poiseuille", 0.95, 5.9, 6.6, 0.6);

  const chips = [
    ["100 ≤ Re ≤ 600", "régimen laminar simulado"],
    ["2D · incompresible", "newtoniano · isotérmico · sin gravedad"],
    ["U = H = 1  →  ν = 1 / Re", "variar la viscosidad es variar Re"],
  ];
  chips.forEach(([big, small], i) => {
    const yy = 1.5 + i * 1.75;
    tarjeta(s, 8.3, yy, 4.4, 1.5, C.paper);
    texto(s, big, 8.6, yy + 0.25, 3.9, 0.6, { fontFace: FUENTE_TITULO, fontSize: 22, bold: true, color: C.navy });
    texto(s, small, 8.6, yy + 0.9, 3.9, 0.4, { fontSize: 14, color: C.grey });
  });
  s.addNotes("Adimensionalización con U (velocidad media de entrada) y H. Re basado en la altura H, "
    + "igual que Armaly et al. y Gartling. Variar ν equivale a variar Re.");
}

// ================= 4. Condiciones =================
{
  const s = nueva("Condiciones iniciales y de frontera", { seccion: "Modelo y método" });
  const cab = (t) => ({ text: t, options: { bold: true, color: C.white, fill: { color: C.navy } } });
  const filas = [
    [cab("Frontera"), cab("Velocidad"), cab("Presión")],
    ["Entrada x = −2H, S < y < H", "Poiseuille u = 6Uη(1−η), v = 0", "∂p/∂n = 0"],
    ["Escalón (tapa y cara vertical)", "u = v = 0 (no deslizamiento)", "∂p/∂n = 0"],
    ["Paredes y = 0 y y = H", "u = v = 0 (no deslizamiento)", "∂p/∂n = 0"],
    ["Salida x = L", "∂u/∂x = ∂v/∂x = 0", "p = 0 (referencia)"],
    ["Condición inicial t = 0", "fluido en reposo u = v = 0", "—"],
  ].map((fila, i) => (i === 0 ? fila : fila.map((c, j) => ({ text: c, options: {
    fill: { color: i % 2 ? C.white : C.paper }, bold: j === 0 } }))));
  s.addTable(filas, { x: 0.6, y: 1.55, w: 12.1, colW: [3.9, 5.2, 3.0], fontFace: FUENTE_TEXTO, fontSize: 16,
    color: C.ink, rowH: 0.62, valign: "middle", border: { type: "none" }, margin: [0.03, 0.139, 0.03, 0.139] });
  texto(s, "La salida fija la referencia de presión y hace no singular la matriz de Poisson. El canal de entrada de 2H "
    + "permite que el perfil se desarrolle antes de la esquina.", 0.6, 5.85, 12.1, 0.8, { fontSize: 15, color: C.grey });
  s.addNotes("La entrada tiene un canal de 2H antes del escalón, como en los estudios de referencia; "
    + "el escalón es un bloque de celdas sólidas.");
}

// ================= 5. Método =================
{
  const s = nueva("Método numérico: 3 pasos por cada Δt", { seccion: "Modelo y método" });
  const tarjetas = [
    ["Velocidad de prueba", ["paso1", "def_A"], "Navier–Stokes sin presión. Adams–Bashforth estima la aceleración a mitad de paso."],
    ["Presión", ["paso2"], "La presión que hace cumplir continuidad. Sale de aplicar divergencia al paso 3."],
    ["Corrección", ["paso3"], "Se corrige la velocidad con el gradiente de presión: ∇·u = 0."],
  ];
  tarjetas.forEach(([t, eqs, d], i) => {
    const x = 0.6 + i * 4.1;
    tarjeta(s, x, 1.5, 3.85, 3.05);
    circulo(s, i + 1, x + 0.3, 1.72, 0.5);
    texto(s, t, x + 0.95, 1.8, 2.8, 0.4, { fontSize: 17, bold: true, color: C.navy });
    let y = 2.5;
    eqs.forEach((e) => { y += ecuacion(s, e, x + 0.3, y, 3.3, 0.55) + 0.12; });
    texto(s, d, x + 0.3, 3.65, 3.3, 0.85, { fontSize: 13, color: C.grey });
  });
  imagen(s, path.join(FIG, "malla_escalonada.png"), 0.6, 4.85, 4.6, 2.0, false);
  texto(s, "Malla escalonada", 0.6, 6.7, 4.6, 0.3, { fontSize: 11, color: C.grey });
  lista(s, [
    "Derivadas → diferencias; valor en la cara = promedio de vecinos",
    "p en el centro de la celda; u y v en sus caras",
    "Poisson: sistema lineal A·p = b, factorizado una sola vez (LU)",
    "Estabilidad: CFL, Δt ≤ Δx / u_max  →  usamos la mitad",
    "Masa conservada: |∇·u| ≈ 10⁻¹⁴",
  ], 5.9, 4.95, 6.8, 1.9, 15);
  s.addNotes("Paso 1: Navier–Stokes sin presión. Paso 2: Poisson para p. Paso 3: corregir. "
    + "CFL: el fluido no avanza más de una celda por paso. Euler simple explota con convección por promedio.");
}

// ================= 6. Caso base =================
{
  const s = nueva("Caso base Re = 200: x_r/S = 4.91", { seccion: "Resultados" });
  tarjeta(s, 0.6, 1.5, 4.1, 5.25, C.paper);
  texto(s, "4.91", 0.95, 1.75, 3.5, 1.3, { fontFace: FUENTE_TITULO, fontSize: 88, bold: true, color: C.coral });
  texto(s, "longitud del remolino, en alturas de escalón (x_r / S)", 0.95, 3.1, 3.5, 0.7, { fontSize: 15, color: C.grey });
  lista(s, ["2 608 pasos · unos 3 s", "Divergencia máxima 8·10⁻¹⁵", "u_max: 1.5 → 0.75 por conservación de masa",
    "Presión sube tras el escalón: gradiente adverso"], 0.95, 4.2, 3.6, 2.4, 14);
  imagen(s, path.join(FIG, "campos_base.png"), 5.0, 1.5, 7.9, 5.2);
  s.addNotes("Leer la figura: velocidad con líneas de corriente, vorticidad (capa de corte) y presión. "
    + "Demo en vivo: cambiar RE en el bloque 0 del notebook y ejecutar.");
}

// ================= 7. Video arranque =================
{
  const s = nueva("Cómo se forma el remolino (tinta virtual)", { seccion: "Resultados" });
  video(s, path.join(FIG, "arranque_re200.mp4"), path.join(EQ, "arranque_re200_portada.png"), 0.6, 1.5, 8.2);
  texto(s, "Qué observar", 9.2, 1.5, 3.5, 0.4, { fontSize: 17, bold: true, color: C.navy });
  const obs = ["Vórtice de arranque en forma de hongo", "Separación pasajera en el techo",
    "x_r crece y se aplana hacia t ≈ 40", "Fluido gris atrapado: eso es la recirculación"];
  obs.forEach((t, i) => {
    const y = 2.1 + i * 1.1;
    circulo(s, i + 1, 9.2, y, 0.42);
    texto(s, t, 9.8, y, 3.0, 0.9, { fontSize: 14, color: C.ink });
  });
  texto(s, "Tablero gris: fluido que ya estaba en el canal. Colores: tinta que entra por cada inyector.",
    0.6, 6.25, 8.2, 0.6, { fontSize: 12, color: C.grey });
  s.addNotes("Reproducir el video (NY = 40). Señalar el vórtice de arranque, la separación pasajera y el fluido atrapado.");
}

// ================= 8. Viscosidad =================
{
  const s = nueva("Efecto de la viscosidad (Re)", { seccion: "Resultados" });
  imagen(s, path.join(FIG, "re_remolinos.png"), 0.6, 1.45, 7.6, 5.4);
  const stats = [
    ["2.8 → 10.1", "x_r/S al pasar de Re 100 a Re 600"],
    ["Re ≈ 400", "aparece la burbuja secundaria en el techo"],
    ["τ_pared = 0", "marca el reacoplamiento en cada caso"],
  ];
  stats.forEach(([big, small], i) => {
    const y = 1.5 + i * 1.8;
    tarjeta(s, 8.6, y, 4.1, 1.55, C.paper);
    texto(s, big, 8.9, y + 0.2, 3.6, 0.6, { fontFace: FUENTE_TITULO, fontSize: 26, bold: true, color: C.teal });
    texto(s, small, 8.9, y + 0.85, 3.6, 0.5, { fontSize: 14, color: C.grey });
  });
  s.addNotes("Al bajar la viscosidad el chorro tarda más en transmitir su momento al piso; el remolino se alarga "
    + "casi proporcional a Re hasta ~400. Después, la burbuja del techo empuja el chorro hacia abajo.");
}

// ================= 9. Video comparativo =================
{
  const s = nueva("Tres viscosidades, un mismo arranque", { seccion: "Resultados" });
  video(s, path.join(FIG, "comparacion_re.mp4"), path.join(EQ, "comparacion_re_portada.png"), 0.6, 1.5, 8.2);
  texto(s, "Qué cambia con Re", 9.2, 1.5, 3.5, 0.4, { fontSize: 17, bold: true, color: C.navy });
  lista(s, ["Re = 100: el flujo se calma hacia t ≈ 20",
    "Re = 300: el remolino crece y se estabiliza",
    "Re = 600: vórtices que viajan y se juntan; aparece la burbuja del techo",
    "Estado final: x_r/S = 2.8, 6.7 y 10.1"], 9.2, 2.05, 3.6, 4.0, 14);
  texto(s, "Gráficas: x_r(t) abajo a la izquierda y velocidad junto al piso a la derecha.",
    0.6, 6.25, 8.2, 0.5, { fontSize: 12, color: C.grey });
  s.addNotes("Reproducir comparacion_re.mp4. Re = 100 se calma rápido; Re = 600 forma varios remolinos y una burbuja en el techo.");
}

// ================= 10. Malla y dt =================
{
  const s = nueva("Malla y paso de tiempo", { seccion: "Validación" });
  s.addChart(pres.charts.BAR, [{ name: "x_r/S", labels: ["10 celdas/H", "20 celdas/H", "40 celdas/H"],
    values: [4.75, 4.91, 4.95] }], {
    x: 0.6, y: 1.5, w: 6.0, h: 4.9, barDir: "col", chartColors: [C.teal], barGapWidthPct: 70,
    showTitle: true, title: "x_r/S frente a la malla (Re = 200)", titleFontFace: FUENTE_TEXTO, titleFontSize: 15,
    titleColor: C.navy, showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 14, dataLabelColor: C.ink,
    dataLabelFormatCode: "0.00", valAxisMinVal: 4.5, valAxisMaxVal: 5.1, valAxisMajorUnit: 0.1,
    valAxisLabelFormatCode: "0.0", catAxisLabelFontSize: 13, valAxisLabelFontSize: 12,
    catAxisLabelColor: C.ink, valAxisLabelColor: C.grey, valGridLine: { color: C.line, size: 0.5 },
    catGridLine: { style: "none" }, showLegend: false, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    dataLabelFontFace: "+mn-lt",
  });
  texto(s, "El eje vertical no empieza en cero para mostrar la diferencia.", 0.6, 6.45, 6.0, 0.4, { fontSize: 11, color: C.grey });

  tarjeta(s, 7.0, 1.5, 5.7, 1.9, C.paper);
  texto(s, "Malla", 7.3, 1.65, 5.0, 0.4, { fontSize: 16, bold: true, color: C.navy });
  texto(s, "De 20 a 40 celdas el resultado cambia 0.7 %: el error con 20 celdas es menor a 1 %.",
    7.3, 2.1, 5.1, 1.0, { fontSize: 14, color: C.ink });

  texto(s, "Paso de tiempo (Re = 200, 20 celdas/H)", 7.0, 3.7, 5.7, 0.4, { fontSize: 16, bold: true, color: C.navy });
  const cab = (t) => ({ text: t, options: { bold: true, color: C.white, fill: { color: C.navy } } });
  s.addTable([
    [cab("Δt / Δt_CFL"), cab("Resultado"), cab("x_r/S")],
    ["0.25", "converge", "4.91"],
    ["0.50", "converge", "4.91"],
    ["0.80", "converge", "4.91"],
    ["1.00", "diverge en 36 pasos", "—"],
    ["Euler (0.50)", "diverge en 706 pasos", "—"],
  ], { x: 7.0, y: 4.15, w: 5.7, colW: [1.8, 2.7, 1.2], fontFace: FUENTE_TEXTO, fontSize: 14, color: C.ink,
    rowH: 0.42, border: { type: "solid", pt: 0.5, color: C.line }, margin: [0.03, 0.111, 0.03, 0.111], valign: "middle" });
  s.addNotes("Duplicar la malla reduce el cambio unas 5 veces: esquema de segundo orden. Dentro del CFL el resultado "
    + "no cambia; en el límite explota; Euler simple explota incluso con la mitad del Δt.");
}

// ================= 11. Literatura =================
{
  const s = nueva("Comparación con la literatura", { seccion: "Validación" });
  const re = ["100", "200", "300", "400", "500", "600"];
  s.addChart(pres.charts.LINE, [
    { name: "Literatura (2D)", labels: re, values: [3.00, 4.95, 6.75, 8.10, 9.30, 10.05] },
    { name: "Este trabajo", labels: re, values: [2.84, 4.91, 6.73, 8.26, 9.40, 10.06] },
  ], {
    x: 0.6, y: 1.5, w: 7.2, h: 5.2, chartColors: [C.grey, C.coral], lineSize: 2.5, lineDataSymbol: "circle",
    lineDataSymbolSize: 9, lineDataSymbolLineColor: C.white,
    showTitle: true, title: "Longitud de reacoplamiento x_r/S contra Re", titleFontFace: FUENTE_TEXTO,
    titleFontSize: 15, titleColor: C.navy, showLegend: true, legendPos: "b", legendFontSize: 13, legendColor: C.ink,
    catAxisTitle: "Re", showCatAxisTitle: true, catAxisTitleFontSize: 13, catAxisTitleColor: C.grey,
    valAxisTitle: "x_r / S", showValAxisTitle: true, valAxisTitleFontSize: 13, valAxisTitleColor: C.grey,
    valAxisMinVal: 2, valAxisMaxVal: 11, valAxisMajorUnit: 1, valAxisLabelFormatCode: "0",
    catAxisLabelFontSize: 13, valAxisLabelFontSize: 12, catAxisLabelColor: C.ink, valAxisLabelColor: C.grey,
    valGridLine: { color: C.line, size: 0.5 }, catGridLine: { style: "none" },
    catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", legendFontFace: "+mn-lt",
  });

  const cab = (t) => ({ text: t, options: { bold: true, color: C.white, fill: { color: C.navy } } });
  const filas = [
    [cab("Re"), cab("Este trabajo"), cab("Literatura"), cab("Dif.")],
    ["100", "2.84", "3.00", "−5.4 %"], ["200", "4.91", "4.95", "−0.7 %"], ["300", "6.73", "6.75", "−0.3 %"],
    ["400", "8.26", "8.10", "+2.0 %"], ["500", "9.40", "9.30", "+1.1 %"], ["600", "10.06", "10.05", "+0.1 %"],
  ];
  s.addTable(filas, { x: 8.2, y: 1.6, w: 4.5, colW: [0.8, 1.35, 1.25, 1.1], fontFace: FUENTE_TEXTO, fontSize: 14,
    color: C.ink, rowH: 0.42, border: { type: "solid", pt: 0.5, color: C.line }, margin: [0.03, 0.083, 0.03, 0.083], valign: "middle",
    align: "center" });
  texto(s, "Para 200 ≤ Re ≤ 600 la diferencia es de 2 % o menos. El error de malla es menor a 1 %, así que la diferencia "
    + "es del orden de la dispersión entre estudios publicados.", 8.2, 4.85, 4.5, 1.5, { fontSize: 13, color: C.grey });
  s.addNotes("Fuente de la tabla de referencia: arXiv:2507.16509 (Tabla 1); la tendencia coincide con Armaly et al. (1983) "
    + "hasta Re ≈ 400.");
}

// ================= 12. Conclusiones =================
{
  const s = nueva("Conclusiones", { oscura: true, seccion: "Conclusiones" });
  const items = [
    ["Navier–Stokes resuelto", "Método de proyección; la masa se conserva a precisión de máquina."],
    ["Física reproducida", "Separación, recirculación, reacoplamiento y remolino del techo a Re ≥ 400."],
    ["Análisis numérico", "Malla: error < 1 %. Δt estable no cambia el resultado; Euler simple explota."],
    ["Validación", "Diferencia de 2 % o menos con la literatura para Re entre 200 y 600."],
  ];
  items.forEach(([t, d], i) => {
    const x = 0.6 + (i % 2) * 6.15, y = 1.6 + Math.floor(i / 2) * 2.45;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 5.95, h: 2.2, rectRadius: 0.12,
      fill: { color: C.navy2 }, line: { type: "none" } });
    texto(s, String(i + 1).padStart(2, "0"), x + 0.35, y + 0.3, 1.2, 0.7,
      { fontFace: FUENTE_TITULO, fontSize: 30, bold: true, color: C.aqua });
    texto(s, t, x + 1.55, y + 0.35, 4.1, 0.5, { fontSize: 19, bold: true, color: C.white });
    texto(s, d, x + 1.55, y + 0.95, 4.1, 1.1, { fontSize: 15, color: "C9D6E3" });
  });
  texto(s, "¡Gracias! Preguntas", 0.6, 6.6, 12.1, 0.5, { fontFace: FUENTE_TITULO, fontSize: 22, bold: true,
    color: C.white, align: "center" });
  s.addNotes("Cierre (1 min) y preguntas. Tener el notebook abierto para la demostración.");
}

pres.writeFile({ fileName: path.join(AQUI, "presentacion.pptx") }).then((f) => console.log("escrito", f));
