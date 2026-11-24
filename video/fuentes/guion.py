# Guion del video: (id, visual, [frases]). Los números van con letra para que la voz los lea bien.
SEGMENTOS = [
    ("titulo", "img:titulo", [
        "Flujo laminar sobre un escalón descendente.",
        "Proyecto final de Mecánica de Fluidos."]),
    ("fenomeno", "img:fenomeno", [
        "Un fluido viaja por un canal y encuentra un escalón: el canal se ensancha al doble.",
        "El fluido se frena, la presión sube, y el fluido lento junto a la pared no puede avanzar contra ese gradiente adverso.",
        "Se separa en la esquina, forma un remolino, y vuelve a tocar el piso en el punto de reacoplamiento."]),
    ("modelo", "img:slide03", [
        "El modelo es flujo bidimensional, incompresible, newtoniano y laminar.",
        "Resolvemos continuidad y Navier Stokes en forma adimensional, con un solo parámetro: el número de Reynolds.",
        "Bajar la viscosidad es subir Reynolds."]),
    ("fronteras", "img:slide04", [
        "En la entrada imponemos el perfil parabólico de Poiseuille.",
        "En las paredes y en el escalón, no deslizamiento.",
        "En la salida, flujo desarrollado y presión cero. El fluido parte del reposo."]),
    ("metodo", "img:slide05", [
        "Cada paso de tiempo se resuelve en tres pasos.",
        "Uno: una velocidad de prueba sin presión, con Adams Bashforth.",
        "Dos: una ecuación de Poisson para la presión que hace cumplir la continuidad.",
        "Tres: corregir la velocidad con el gradiente de presión."]),
    ("codigo_a", "rec:inicio:parametros+2", [
        "Así corremos el código en Jupyter. Los parámetros están al inicio."]),
    ("codigo_b", "rec:parametros+2:salida_base", [
        "Cada función hace una tarea: la malla, la matriz de presión, las fronteras, la convección y difusión, y el ciclo de tres pasos."]),
    ("codigo_c", "rec:salida_base:editar", [
        "El caso base, con Reynolds doscientos, converge en unos tres segundos.",
        "La masa se conserva, y el remolino mide cuatro punto nueve alturas de escalón."]),
    ("codigo_d", "rec:editar:corre_400", [
        "Probamos otro parámetro: Reynolds cuatrocientos."]),
    ("codigo_e", "rec:corre_400:salida_400", []),
    ("codigo_f", "rec:salida_400:fin", [
        "Con menos viscosidad, el remolino crece a ocho punto tres alturas de escalón."]),
    ("arranque", "vid:arranque_re200.mp4", [
        "Esta es la simulación del arranque, con tinta virtual.",
        "La capa de corte se enrolla en un vórtice que viaja aguas abajo.",
        "El remolino crece hasta su largo final, y el fluido gris queda atrapado girando: eso es la recirculación."]),
    ("reynolds", "vid:comparacion_re.mp4", [
        "Al bajar la viscosidad el remolino se alarga: de dos punto ocho alturas de escalón en Reynolds cien, a diez en Reynolds seiscientos.",
        "Desde Reynolds cuatrocientos aparece un segundo remolino en el techo."]),
    ("malla_dt", "img:slide10", [
        "Al duplicar la malla, el resultado cambia menos de uno por ciento.",
        "El paso de tiempo no cambia el resultado mientras sea estable; en el límite de Courant, la solución explota."]),
    ("validacion", "img:slide11", [
        "Frente a la literatura, la diferencia es de dos por ciento o menos entre Reynolds doscientos y seiscientos."]),
    ("cierre", "img:cierre", [
        "En resumen: resolvimos Navier Stokes, reprodujimos la separación, la recirculación y el reacoplamiento, y validamos el resultado.",
        "Gracias."]),
]
