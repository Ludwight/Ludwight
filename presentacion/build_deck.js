// Genera presentacion.pptx (12 diapositivas, versión simple) con pptxgenjs.
// Uso (desde presentacion/):  npm install  →  python render_eqs.py  →  node build_deck.js  →  python transiciones.py presentacion.pptx
// Requiere que el notebook ya haya generado ../figures/*.png y ../figures/*.mp4.
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const AQUI = __dirname;
const FIG = path.join(AQUI, "..", "figures");
const EQ = path.join(AQUI, "eq");

const C = {
  navy: "0B1F3A", navy2: "1A3457", teal: "0E7C86", aqua: "7FD1D6", coral: "F26B3A", green: "2E9E5B", red: "C8423B",
  ink: "1E2A38", grey: "5B6878", paper: "F4F7FA", white: "FFFFFF", line: "D5DEE8", step: "6B7685",
};
const TIT = "Cambria";
const TXT = "Calibri";

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
pres.layout = "LAYOUT_WIDE";                       // 13.33 × 7.5 in
pres.author = "Luis Antonio Pérez Hernández · Marco Antonio Navarrete Baños";
pres.title = "Flujo laminar sobre un escalón descendente";
pres.theme = { headFontFace: TIT, bodyFontFace: TXT };

pres.defineSlideMaster({
  title: "CONTENIDO",
  background: { color: C.white },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.1, h: 0.9, valign: "middle",
      fontFace: TIT, fontSize: 32, bold: true, color: C.navy, align: "left", margin: 0 }, text: "" } },
    { text: { text: "Flujo sobre un escalón descendente · Mecánica de Fluidos", options: { x: 0.6, y: 7.0, w: 9, h: 0.3,
      fontFace: TXT, fontSize: 10, color: "8A96A6", margin: 0 } } },
  ],
  slideNumber: { x: 12.2, y: 7.0, w: 0.5, h: 0.3, fontFace: TXT, fontSize: 10, color: "8A96A6", align: "right" },
});
pres.defineSlideMaster({
  title: "PORTADA",
  background: { color: C.navy },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.75, w: 6.2, h: 2.0, valign: "top",
      fontFace: TIT, fontSize: 42, bold: true, color: C.white, margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "OSCURA",
  background: { color: C.navy },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.1, h: 0.9, valign: "middle",
      fontFace: TIT, fontSize: 32, bold: true, color: C.white, align: "left", margin: 0 }, text: "" } },
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
function etiqueta(s, t, x, y, w) {        // pequeña etiqueta de sección arriba del título
  s.addText(t.toUpperCase(), { x, y, w, h: 0.3, fontFace: TXT, fontSize: 11, bold: true, color: C.teal, margin: 0,
    charSpacing: 1 });
}
function circulo(s, n, x, y, d = 0.5, color = C.teal) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color }, line: { type: "none" } });
  s.addText(String(n), { x, y, w: d, h: d, align: "center", valign: "middle", fontFace: TXT,
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
function lista(s, items, x, y, w, h, tam = 16, color = C.ink) {
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })),
    { x, y, w, h, fontFace: TXT, fontSize: tam, color, valign: "top", paraSpaceAfter: 8, margin: 0 });
}
function texto(s, t, x, y, w, h, o = {}) {
  s.addText(t, Object.assign({ x, y, w, h, fontFace: TXT, fontSize: 16, color: C.ink, valign: "top", margin: 0 }, o));
}
function numero(s, grande, chico, x, y, w, h, color = C.coral) {   // tarjeta con un número grande
  tarjeta(s, x, y, w, h, C.paper);
  texto(s, grande, x + 0.25, y + 0.2, w - 0.5, h * 0.5, { fontFace: TIT, fontSize: 34, bold: true, color, valign: "middle" });
  texto(s, chico, x + 0.25, y + 0.2 + h * 0.5, w - 0.5, h * 0.45 - 0.2, { fontSize: 14, color: C.grey });
}
function flecha(s, x, y, w) {
  s.addShape(pres.shapes.RIGHT_ARROW, { x, y, w, h: 0.32, fill: { color: C.teal }, line: { type: "none" } });
}

// ================= 1. Portada =================
{
  const s = pres.addSlide({ masterName: "PORTADA", sectionTitle: declarar("Presentación") });
  s.addText("Flujo laminar sobre un escalón descendente", { placeholder: "title" });
  texto(s, "PROYECTO FINAL · MECÁNICA DE FLUIDOS", 0.6, 1.2, 6.4, 0.4, { fontSize: 13, bold: true, color: C.aqua });
  texto(s, "Simulación numérica de Navier–Stokes en Python", 0.6, 3.85, 6.0, 0.6, { fontSize: 19, color: "C9D6E3" });
  texto(s, "Luis Antonio Pérez Hernández\nMarco Antonio Navarrete Baños", 0.6, 5.2, 6.0, 0.8,
    { fontSize: 16, color: C.white, paraSpaceAfter: 4 });
  texto(s, "Prof. Anuar Sánchez", 0.6, 6.3, 6.0, 0.4, { fontSize: 13, color: "9FB0C4" });
  imagen(s, path.join(EQ, "arranque_re200_portada.png"), 7.1, 2.0, 5.6, 3.6, false);
  s.addNotes("AMBOS (0:30). LUIS: presentarse; simulamos con un código propio cómo fluye un fluido al pasar por un escalón. "
    + "MARCO: orden: el problema físico, las ecuaciones, cómo lo resolvemos en la computadora, los resultados y conclusiones.");
}

// ================= 2. El fenómeno =================
{
  const s = nueva("¿Qué estudiamos?", { seccion: "1. Física del fenómeno" });
  etiqueta(s, "1 · Física del fenómeno", 0.6, 0.12, 6);
  texto(s, [
    { text: "En esta simulación se modela numéricamente ", options: {} },
    { text: "el flujo de un fluido viscoso que pasa por un escalón", options: { bold: true } },
    { text: ": el canal se ensancha de golpe al doble.", options: {} },
  ], 0.6, 1.4, 12.1, 0.7, { fontSize: 19 });
  imagen(s, path.join(FIG, "fenomeno_anotado.png"), 0.6, 2.2, 8.1, 4.5);
  const pasos = [
    ["Se separa", "En la esquina el fluido no puede dar la vuelta."],
    ["Forma un remolino", "Detrás del escalón el fluido gira y regresa."],
    ["Se vuelve a pegar", "Más adelante toca el piso otra vez: punto de reacoplamiento x_r."],
  ];
  pasos.forEach(([t, d], i) => {
    const y = 2.35 + i * 1.45;
    circulo(s, i + 1, 9.1, y);
    texto(s, t, 9.8, y, 3.0, 0.4, { fontSize: 18, bold: true, color: C.navy });
    texto(s, d, 9.8, y + 0.42, 3.0, 0.9, { fontSize: 14, color: C.grey });
  });
  s.addNotes("LUIS (1:30). Leer la frase de arriba con sus palabras. Señalar en la figura: la esquina (se separa), "
    + "el remolino (el fluido gira al revés) y el triángulo rojo (se vuelve a pegar). ¿Por qué se separa? Al ensancharse el canal "
    + "el fluido se frena y la presión sube; el fluido lento junto a la pared no puede avanzar contra esa presión. "
    + "Lo que medimos es x_r, el largo del remolino.");
}

// ================= 3. Variables y parámetros =================
{
  const s = nueva("Variables y parámetros del modelo", { seccion: "1. Física del fenómeno" });
  etiqueta(s, "1 · Física del fenómeno", 0.6, 0.12, 6);
  const cols = [
    ["Lo que calculamos", [["u, v", "velocidad en x y en y"], ["p", "presión"]]],
    ["El parámetro físico", null],
    ["Lo que elegimos para calcular", [["Δx = 0.05", "tamaño de cada celda (20 por altura)"], ["Δt = 0.017", "paso de tiempo"]]],
  ];
  cols.forEach(([titulo, items], i) => {
    const x = 0.6 + i * 4.1;
    tarjeta(s, x, 1.5, 3.85, 4.4, C.paper);
    texto(s, titulo, x + 0.3, 1.7, 3.3, 0.4, { fontSize: 17, bold: true, color: C.teal });
    if (items) {
      items.forEach(([sim, desc], k) => {
        texto(s, sim, x + 0.3, 2.4 + k * 1.6, 3.3, 0.7, { fontFace: TIT, fontSize: 32, bold: true, color: C.navy });
        texto(s, desc, x + 0.3, 3.1 + k * 1.6, 3.3, 0.6, { fontSize: 15, color: C.grey });
      });
    } else {
      eq(s, "re_def", x + 0.3, 2.35, 3.3, 1.2);
      texto(s, "Número de Reynolds: inercia contra viscosidad", x + 0.3, 3.75, 3.3, 0.6, { fontSize: 15, color: C.grey });
      texto(s, "Bajar la viscosidad ν es lo mismo que subir Re", x + 0.3, 4.55, 3.3, 0.8,
        { fontSize: 16, bold: true, color: C.coral });
    }
  });
  texto(s, "Geometría: el escalón mide la mitad de la altura H, así que el canal pasa de H/2 a H. Usamos U = H = 1, "
    + "y probamos Re = 100 a 600.", 0.6, 6.15, 12.1, 0.6, { fontSize: 15, color: C.grey });
  s.addNotes("LUIS (1:15). Incógnitas: u, v y p en cada punto y cada instante. Un solo parámetro físico, Re = UH/ν: "
    + "con U = H = 1, ν = 1/Re, así que estudiar la viscosidad es estudiar Re. Parámetros numéricos: tamaño de celda y paso de tiempo.");
}

// ================= 4. Ecuaciones de gobierno =================
{
  const s = nueva("Ecuaciones de gobierno y supuestos", { seccion: "2. Idea matemática" });
  etiqueta(s, "2 · Idea matemática", 0.6, 0.12, 6);
  tarjeta(s, 0.6, 1.5, 8.0, 5.2, C.paper);
  texto(s, "Continuidad", 0.95, 1.7, 7.3, 0.4, { fontSize: 17, bold: true, color: C.teal });
  eq(s, "cont_simple", 0.95, 2.15, 7.3, 1.0);
  texto(s, "Navier–Stokes (cantidad de movimiento)", 0.95, 3.45, 7.3, 0.4, { fontSize: 17, bold: true, color: C.teal });
  eq(s, "ns_simple", 0.95, 3.95, 7.3, 1.4);
  texto(s, "Son las ecuaciones de clase, escritas sin unidades: así sólo queda Re.", 0.95, 5.85, 7.3, 0.6,
    { fontSize: 14, color: C.grey });
  texto(s, "Supuestos", 9.0, 1.5, 3.7, 0.4, { fontSize: 18, bold: true, color: C.navy });
  lista(s, ["2D: el canal es muy ancho", "Incompresible: ρ constante", "Newtoniano: μ constante",
    "Laminar: Re ≤ 600", "Sin gravedad ni temperatura"], 9.0, 2.05, 3.7, 4.5, 16);
  s.addNotes("LUIS (1:45). Continuidad: lo que entra a una celda sale; no se crea ni se pierde masa. Navier–Stokes es F = ma "
    + "para un fluido: aceleración = fuerza de presión + fuerza viscosa. Escrita sin unidades, la viscosidad aparece como 1/Re. "
    + "Supuestos: 2D, incompresible, newtoniano, laminar (la transición es alrededor de Re = 1200) y sin gravedad, que sólo "
    + "agrega presión hidrostática.");
}

// ================= 5. Condiciones iniciales y de frontera (esquema) =================
{
  const s = nueva("Condiciones iniciales y de frontera", { seccion: "2. Idea matemática" });
  etiqueta(s, "2 · Idea matemática", 0.6, 0.12, 6);
  // esquema del canal (no está a escala)
  const x0 = 2.4, x1 = 4.0, x2 = 10.0, yT = 2.3, yM = 3.55, yB = 4.8;
  s.addShape(pres.shapes.RECTANGLE, { x: x0, y: yT, w: x2 - x0, h: yM - yT, fill: { color: "E6F4F5" }, line: { type: "none" } });
  s.addShape(pres.shapes.RECTANGLE, { x: x1, y: yM, w: x2 - x1, h: yB - yM, fill: { color: "E6F4F5" }, line: { type: "none" } });
  s.addShape(pres.shapes.RECTANGLE, { x: x0, y: yM, w: x1 - x0, h: yB - yM, fill: { color: C.step }, line: { type: "none" } });
  s.addShape(pres.shapes.LINE, { x: x0, y: yT, w: x2 - x0, h: 0, line: { color: C.navy, width: 3 } });
  s.addShape(pres.shapes.LINE, { x: x1, y: yB, w: x2 - x1, h: 0, line: { color: C.navy, width: 3 } });
  s.addShape(pres.shapes.LINE, { x: x0, y: yM, w: x1 - x0, h: 0, line: { color: C.navy, width: 3 } });
  s.addShape(pres.shapes.LINE, { x: x1, y: yM, w: 0, h: yB - yM, line: { color: C.navy, width: 3 } });
  s.addShape(pres.shapes.LINE, { x: x2, y: yT, w: 0, h: yB - yT, line: { color: C.coral, width: 2, dashType: "dash" } });
  // flechas del perfil parabólico en la entrada
  [0.25, 0.5, 0.75].forEach((e, k) => {
    const largo = 0.25 + 1.2 * 4 * e * (1 - e);
    s.addShape(pres.shapes.RIGHT_ARROW, { x: x0 - largo - 0.05, y: yT + e * (yM - yT) - 0.11, w: largo, h: 0.22,
      fill: { color: C.teal }, line: { type: "none" } });
  });
  texto(s, "escalón", x0, yM + 0.45, x1 - x0, 0.4, { fontSize: 14, color: C.white, align: "center", bold: true });
  // etiquetas
  texto(s, "ENTRADA", 0.6, 1.5, 3.0, 0.3, { fontSize: 13, bold: true, color: C.teal });
  texto(s, "perfil parabólico, v = 0", 0.6, 1.8, 3.0, 0.3, { fontSize: 13, color: C.grey });
  eq(s, "entrada_simple", 0.6, 4.95, 1.75, 0.4);
  texto(s, "PAREDES Y ESCALÓN", 4.9, 1.5, 4.5, 0.3, { fontSize: 13, bold: true, color: C.navy });
  texto(s, "u = v = 0: el fluido se pega a la pared (no deslizamiento)", 4.9, 1.8, 5.1, 0.3, { fontSize: 13, color: C.grey });
  texto(s, "SALIDA", 10.25, 2.6, 2.5, 0.3, { fontSize: 13, bold: true, color: C.coral });
  texto(s, "p = 0 y el flujo ya no cambia en x (∂u/∂x = 0)", 10.25, 2.9, 2.45, 0.9, { fontSize: 13, color: C.grey });
  // condición inicial
  tarjeta(s, 0.6, 5.7, 12.1, 0.95, C.navy);
  texto(s, [
    { text: "Condición inicial (t = 0): ", options: { bold: true, color: C.aqua } },
    { text: "el fluido está quieto, u = v = 0. Avanzamos en el tiempo hasta que el flujo deja de cambiar.",
      options: { color: C.white } },
  ], 0.95, 5.92, 11.5, 0.6, { fontSize: 17 });
  s.addNotes("LUIS (1:30). Recorrer el dibujo de izquierda a derecha. Entrada: perfil parabólico de Poiseuille, el de un canal "
    + "largo; el 6 hace que la velocidad media sea U. Paredes y escalón: no deslizamiento, u = v = 0. Salida: p = 0 como "
    + "referencia y flujo desarrollado; por eso el canal es largo (hasta 25H). Inicio: fluido en reposo. "
    + "Pasar la palabra: «Marco, ¿cómo resolvemos esto en la computadora?»");
}

// ================= 6. Discretización =================
{
  const s = nueva("De ecuaciones a números: la malla", { seccion: "3. Metodología y código" });
  etiqueta(s, "3 · Metodología y código", 0.6, 0.12, 6);
  imagen(s, path.join(FIG, "malla_escalonada.png"), 0.6, 1.5, 5.6, 4.6, false);
  const ideas = [
    ["Dividimos el canal en celdas", "Cuadros de lado Δx: 20 en la altura."],
    ["Cada variable en su lugar", "p en el centro de la celda; u y v en las caras (malla escalonada)."],
    ["Derivada → diferencia", null],
  ];
  ideas.forEach(([t, d], i) => {
    const y = 1.55 + i * 1.45;
    circulo(s, i + 1, 6.7, y);
    texto(s, t, 7.4, y, 5.3, 0.4, { fontSize: 18, bold: true, color: C.navy });
    if (d) texto(s, d, 7.4, y + 0.45, 5.3, 0.8, { fontSize: 15, color: C.grey });
    else eq(s, "deriv_simple", 7.4, y + 0.45, 4.0, 0.75);
  });
  tarjeta(s, 6.7, 5.95, 6.0, 0.75, C.paper);
  texto(s, "Así cada ecuación se vuelve una cuenta con los vecinos de cada celda.", 6.95, 6.1, 5.6, 0.5,
    { fontSize: 14, color: C.ink });
  s.addNotes("MARCO (1:30). La computadora no deriva, resta. Partimos el canal en celdas y cambiamos cada derivada por una "
    + "diferencia entre vecinos. Malla escalonada: la velocidad de cada cara queda justo entre dos presiones, y la fuerza "
    + "de presión es la diferencia de esas dos. El escalón son celdas sólidas.");
}

// ================= 7. Método de proyección =================
{
  const s = nueva("El método: tres pasos en cada Δt", { seccion: "3. Metodología y código" });
  etiqueta(s, "3 · Metodología y código", 0.6, 0.12, 6);
  const pasos = [
    ["Velocidad de prueba", "paso1_simple", "Se mueve el fluido con convección y viscosidad, sin presión."],
    ["Presión", "paso2", "Se calcula la presión que hace que no se cree ni se pierda masa."],
    ["Corrección", "paso3", "Se corrige la velocidad con esa presión."],
  ];
  pasos.forEach(([t, e, d], i) => {
    const x = 0.6 + i * 4.1;
    tarjeta(s, x, 1.5, 3.85, 3.6);
    circulo(s, i + 1, x + 0.3, 1.75);
    texto(s, t, x + 0.95, 1.8, 2.8, 0.45, { fontSize: 18, bold: true, color: C.navy });
    eq(s, e, x + 0.3, 2.55, 3.25, 0.85);
    texto(s, d, x + 0.3, 3.65, 3.25, 1.2, { fontSize: 15, color: C.grey });
    if (i < 2) flecha(s, x + 3.88, 3.0, 0.2);
  });
  tarjeta(s, 0.6, 5.4, 12.1, 1.3, C.navy);
  texto(s, [
    { text: "Método de proyección (Chorin, 1968). ", options: { bold: true, color: C.aqua } },
    { text: "Se repite paso a paso desde el reposo hasta el estado estacionario. Para que sea estable, A se estima a la mitad "
      + "del paso con la aceleración actual y la anterior (Adams–Bashforth).", options: { color: C.white } },
  ], 0.95, 5.6, 11.5, 0.95, { fontSize: 16 });
  s.addNotes("MARCO (1:45). Problema: la presión no tiene su propia ecuación. Paso 1: velocidad de prueba sin presión. "
    + "Paso 2: la presión que hace cumplir continuidad; sale de pedir que la divergencia de la velocidad corregida sea cero "
    + "(ecuación de Poisson). Paso 3: corregir. Euler simple explota; Adams–Bashforth usa también la aceleración anterior "
    + "y es estable (lo veremos en la demo).");
}

// ================= 8. Estructura del código =================
{
  const s = nueva("El código en Python", { seccion: "3. Metodología y código" });
  etiqueta(s, "3 · Metodología y código", 0.6, 0.12, 6);
  const cajas = [
    ["Parámetros", "RE, NY, L"],
    ["Malla", "crear_malla"],
    ["Matriz de presión", "matriz_presion"],
    ["Ciclo en el tiempo", "simular\n(pasos 1, 2 y 3)"],
    ["Resultados", "x_r, gráficas, videos"],
  ];
  const w = 2.15, gap = 0.34;
  cajas.forEach(([t, f], i) => {
    const x = 0.6 + i * (w + gap);
    const color = i === 3 ? C.navy : C.paper;
    tarjeta(s, x, 2.0, w, 1.7, color);
    texto(s, t, x + 0.15, 2.2, w - 0.3, 0.7, { fontSize: 17, bold: true, color: i === 3 ? C.white : C.navy, align: "center" });
    texto(s, f, x + 0.15, 2.95, w - 0.3, 0.6, { fontFace: "Courier New", fontSize: 12, color: i === 3 ? C.aqua : C.teal,
      align: "center" });
    if (i < cajas.length - 1) flecha(s, x + w + 0.02, 2.69, gap - 0.04);
  });
  s.addShape(pres.shapes.CIRCULAR_ARROW, { x: 8.1, y: 3.75, w: 0.9, h: 0.9, fill: { color: C.coral }, line: { type: "none" },
    rotate: 180 });
  texto(s, "se repite miles de veces", 9.05, 3.95, 2.6, 0.4, { fontSize: 13, color: C.coral, bold: true });
  lista(s, [
    "Un solo notebook que corre completo con «Ejecutar todo» (~5 min con videos).",
    "Librerías: numpy (cuentas), scipy (sistema de la presión) y matplotlib (gráficas y videos).",
    "Cada análisis es la misma función simular(Re, NY, dt) con otros valores.",
  ], 0.6, 4.9, 12.1, 1.8, 16);
  s.addNotes("MARCO (1:15). Recorrer las cajas: parámetros al inicio; la malla; la matriz de presión, que se arma una vez; "
    + "el ciclo con los tres pasos, que se repite miles de veces; y al final x_r, gráficas y videos. "
    + "«Ahora lo vemos correr.» → DEMO (2:30): RE = 400 (8.26, ~8 s, burbuja en el techo); "
    + "simular(200, dt=(H/20)/1.5, t_max=150) explota en 36 pasos; simular(200, ab2=False, t_max=150) explota en 706. "
    + "Regresar RE = 200.");
}

// ================= 9. Caso base =================
{
  const s = nueva("Resultado: caso base Re = 200", { seccion: "4. Resultados y análisis" });
  etiqueta(s, "4 · Resultados y análisis paramétrico", 0.6, 0.12, 8);
  imagen(s, path.join(FIG, "campos_base.png"), 0.6, 1.5, 7.9, 5.2);
  numero(s, "4.91", "largo del remolino, en alturas de escalón (x_r/S)", 8.9, 1.5, 3.8, 1.75);
  numero(s, "≈ 0", "∇·u ≈ 10⁻¹⁵: la masa se conserva", 8.9, 3.45, 3.8, 1.5, C.teal);
  texto(s, "Arriba: velocidad. En medio: vorticidad (giro). Abajo: presión, que sube después del escalón.",
    8.9, 5.2, 3.8, 1.4, { fontSize: 14, color: C.grey });
  s.addNotes("MARCO (1:15). Leer la figura: el chorro sale del canal de entrada y abajo queda el remolino. La vorticidad se "
    + "concentra en la capa que separa chorro y remolino. La presión sube tras el escalón: esa es la causa de la separación. "
    + "x_r = 4.91 alturas de escalón; la divergencia es prácticamente cero.");
}

// ================= 10. Viscosidad y velocidad =================
{
  const s = nueva("¿Qué pasa si cambiamos la viscosidad?", { seccion: "4. Resultados y análisis" });
  etiqueta(s, "4 · Resultados y análisis paramétrico", 0.6, 0.12, 8);
  video(s, path.join(FIG, "comparacion_re.mp4"), path.join(EQ, "comparacion_re_portada.png"), 0.6, 1.5, 7.6);
  numero(s, "2.8", "Re = 100 (más viscoso)", 8.6, 1.5, 4.1, 1.25, C.teal);
  numero(s, "6.7", "Re = 300", 8.6, 2.9, 4.1, 1.25, C.teal);
  numero(s, "10.1", "Re = 600 (menos viscoso)", 8.6, 4.3, 4.1, 1.25, C.coral);
  texto(s, "Largo del remolino x_r/S. Menos viscosidad → remolino más largo; desde Re ≈ 400 aparece otro en el techo. "
    + "Más velocidad de entrada es lo mismo que más Re.", 8.6, 5.75, 4.1, 1.2, { fontSize: 13, color: C.grey });
  s.addNotes("MARCO (1:30). Reproducir el video: tres arranques a la vez. Con menos viscosidad el chorro tarda más en "
    + "transmitir su movimiento al piso, así que se vuelve a pegar más lejos: 2.8 → 6.7 → 10.1. Desde Re ≈ 400 se separa "
    + "también el techo. Velocidad: como Re = UH/ν, subir U es lo mismo que subir Re (en agua y un canal de 1 cm, "
    + "Re 100–600 son 1–6 cm/s).");
}

// ================= 11. Estabilidad: dt y malla =================
{
  const s = nueva("Estabilidad: paso de tiempo y malla", { seccion: "4. Resultados y análisis" });
  etiqueta(s, "4 · Resultados y análisis paramétrico", 0.6, 0.12, 8);
  texto(s, "Paso de tiempo Δt", 0.6, 1.45, 6.0, 0.4, { fontSize: 19, bold: true, color: C.navy });
  eq(s, "cfl", 0.6, 1.95, 2.6, 0.9);
  texto(s, "Condición CFL: en un paso el fluido no debe avanzar más de una celda.", 3.4, 2.05, 3.2, 0.9,
    { fontSize: 14, color: C.grey });
  const casos = [
    ["✓", "Δt menor al límite", "mismo resultado (4.91)", C.green],
    ["✗", "Δt en el límite", "explota en 36 pasos", C.red],
    ["✗", "Euler en vez de Adams–Bashforth", "explota en 706 pasos", C.red],
  ];
  casos.forEach(([icono, t, r, color], i) => {
    const y = 3.15 + i * 1.18;
    tarjeta(s, 0.6, y, 6.0, 1.0, C.paper);
    texto(s, icono, 0.8, y + 0.15, 0.6, 0.7, { fontSize: 30, bold: true, color, valign: "middle" });
    texto(s, t, 1.5, y + 0.12, 5.0, 0.4, { fontSize: 16, bold: true, color: C.navy });
    texto(s, r, 1.5, y + 0.52, 5.0, 0.4, { fontSize: 15, color });
  });
  texto(s, "Tamaño de malla", 7.0, 1.45, 5.7, 0.4, { fontSize: 19, bold: true, color: C.navy });
  s.addChart(pres.charts.BAR, [{ name: "x_r/S", labels: ["10 celdas", "20 celdas", "40 celdas"], values: [4.75, 4.91, 4.95] }], {
    x: 7.0, y: 1.95, w: 5.7, h: 3.6, barDir: "col", chartColors: [C.teal], barGapWidthPct: 60,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 16, dataLabelColor: C.ink, dataLabelFormatCode: "0.00",
    valAxisMinVal: 4.5, valAxisMaxVal: 5.1, valAxisHidden: true, valGridLine: { style: "none" },
    catAxisLabelFontSize: 14, catAxisLabelColor: C.ink, catGridLine: { style: "none" }, showLegend: false,
    catAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt",
  });
  tarjeta(s, 7.0, 5.7, 5.7, 1.0, C.paper);
  texto(s, "Al duplicar las celdas el resultado cambia menos de 1 %: la malla de 20 es suficiente.", 7.25, 5.85, 5.3, 0.75,
    { fontSize: 15, color: C.ink });
  s.addNotes("LUIS (1:30). Δt: mientras se respete el CFL el resultado es el mismo, sólo cambia el número de pasos; en el "
    + "límite explota (lo vimos en la demo), y Euler simple explota aunque Δt sea chico. Malla: 10, 20 y 40 celdas dan 4.75, "
    + "4.91 y 4.95; de 20 a 40 cambia menos de 1 %. (El eje no empieza en cero para que se vea la diferencia.)");
}

// ================= 12. Conclusiones =================
{
  const s = nueva("Conclusiones", { oscura: true, seccion: "5. Conclusiones" });
  const cols = [
    ["Interpretación física", ["El escalón frena el fluido y sube la presión: por eso se separa.",
      "Menos viscosidad → remolino más largo (2.8 a 10.1 alturas de escalón).",
      "Desde Re ≈ 400 aparece un segundo remolino en el techo."]],
    ["Alcances", ["Resuelve Navier–Stokes 2D desde el reposo; la masa se conserva.",
      "Estable si se respeta el CFL; la malla de 20 da error < 1 %.",
      "Coincide con la literatura (diferencia ≤ 2 %)."]],
    ["Limitaciones", ["Sólo 2D: el flujo real se vuelve 3D por arriba de Re ≈ 400.",
      "Sólo laminar: no sirve cerca de la turbulencia (Re ≈ 1200).",
      "Para Re alto haría falta una malla más fina."]],
  ];
  cols.forEach(([t, items], i) => {
    const x = 0.6 + i * 4.1;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.45, w: 3.85, h: 4.8, rectRadius: 0.1, fill: { color: C.navy2 },
      line: { type: "none" } });
    texto(s, t, x + 0.3, 1.65, 3.3, 0.45, { fontSize: 19, bold: true, color: C.aqua });
    lista(s, items, x + 0.3, 2.3, 3.3, 3.8, 15, "E3EAF2");
  });
  texto(s, "¡Gracias! Preguntas", 0.6, 6.45, 12.1, 0.5, { fontFace: TIT, fontSize: 22, bold: true, color: C.white,
    align: "center" });
  s.addNotes("AMBOS (1:00). LUIS: interpretación física (gradiente adverso, viscosidad, remolino del techo). "
    + "MARCO: alcances y limitaciones. Cerrar: «Muchas gracias, ¿tienen preguntas?»");
}

pres.writeFile({ fileName: path.join(AQUI, "presentacion.pptx") }).then((f) => console.log("escrito", f));
