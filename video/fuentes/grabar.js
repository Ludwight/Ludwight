// Graba JupyterLab ejecutando el notebook de demostración. Uso: node grabar.js <token>
const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const token = process.argv[2];
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    recordVideo: { dir: __dirname + '/grabacion', size: { width: 1920, height: 1080 } },
  });
  const page = await context.newPage();
  const t0 = Date.now();
  const eventos = [];
  const marca = (nombre) => { eventos.push([nombre, (Date.now() - t0) / 1000]); console.log(nombre, (Date.now() - t0) / 1000); };
  const espera = (ms) => page.waitForTimeout(ms);

  await page.goto(`http://127.0.0.1:8890/lab/tree/escalon_descendente.ipynb?token=${token}`);
  await page.waitForSelector('.jp-Notebook .jp-Cell', { timeout: 60000 });
  await page.addStyleTag({ content: `:root { --jp-code-font-size: 19px !important; --jp-content-font-size1: 19px !important;
    --jp-content-font-size2: 22px !important; --jp-content-font-size3: 26px !important; --jp-content-font-size4: 30px !important;
    --jp-content-font-size5: 34px !important; --jp-ui-font-size1: 15px !important; --jp-code-line-height: 1.3 !important; }` });
  await espera(4000);
  // cerrar la barra lateral y avisos
  const lateral = await page.evaluate(() => { const e = document.querySelector('#jp-left-stack'); return !!e && e.offsetWidth > 0; });
  if (lateral) await page.keyboard.press('Control+b');
  await page.evaluate(() => document.querySelectorAll('.jp-Notification-Toast-Close, .Toastify__close-button').forEach(b => b.click()));
  await espera(1500);

  // desplazamiento suave del contenedor del notebook hasta un elemento
  const suave = async (selector, indice, ms, desfase = 80) => {
    await page.evaluate(async ([selector, indice, ms, desfase]) => {
      const el = document.querySelectorAll(selector)[indice];
      let sc = el.parentElement;
      while (sc && !(sc.scrollHeight > sc.clientHeight + 5 && getComputedStyle(sc).overflowY !== 'visible')) sc = sc.parentElement;
      const ini = sc.scrollTop;
      const fin = ini + el.getBoundingClientRect().top - sc.getBoundingClientRect().top - desfase;
      const t = performance.now();
      await new Promise(res => {
        const paso = (ahora) => {
          const f = Math.min(1, (ahora - t) / ms), s = 0.5 - 0.5 * Math.cos(Math.PI * f);
          sc.scrollTop = ini + (fin - ini) * s;
          f < 1 ? requestAnimationFrame(paso) : res();
        };
        requestAnimationFrame(paso);
      });
    }, [selector, indice, ms, desfase]);
  };
  const indiceCelda = (texto) => page.evaluate((texto) =>
    [...document.querySelectorAll('.jp-Notebook .jp-Cell')].findIndex(c => c.innerText.includes(texto)), texto);

  marca('inicio');
  await espera(2500);

  // Ejecutar todo (menú Run → Run All Cells)
  await page.click('.lm-MenuBar-itemLabel:text-is("Run")');
  await espera(700);
  await page.click('.lm-Menu-itemLabel:text-is("Run All Cells")');
  marca('run_all');

  // recorrer el código mientras corre
  const iParam = await indiceCelda('PARÁMETROS (cambiar aquí');
  await suave('.jp-Notebook .jp-Cell', iParam, 2500);
  marca('parametros'); await espera(3500);
  for (const texto of ['def matriz_presion', 'def fronteras', 'def aceleracion_u', 'def simular']) {
    const i = await indiceCelda(texto);
    await suave('.jp-Notebook .jp-Cell', i, 2200);
    marca(texto); await espera(texto === 'def simular' ? 6000 : 2800);
  }
  const iBase = await indiceCelda('base = simular(RE');
  await page.waitForFunction((i) => document.querySelectorAll('.jp-Notebook .jp-Cell')[i].querySelector('.jp-OutputArea').innerText.includes('Reacoplamiento'),
                             iBase, { timeout: 120000 });
  await suave('.jp-Notebook .jp-Cell', iBase, 2500);
  marca('salida_base'); await espera(5000);
  await page.waitForFunction((i) => document.querySelectorAll('.jp-Notebook .jp-Cell')[i + 1].querySelectorAll('img').length >= 2,
                             iBase, { timeout: 120000 });
  await suave('.jp-Notebook .jp-Cell', iBase + 1, 2500, 40);
  marca('figura_base'); await espera(6000);

  // cambiar RE a 400 y volver a correr
  await suave('.jp-Notebook .jp-Cell', iParam, 2500);
  marca('editar'); await espera(1200);
  const linea = page.locator('.jp-Notebook .jp-Cell').nth(iParam).locator('.cm-line', { hasText: 'RE = 200' });
  await linea.click({ position: { x: 5, y: 8 } });
  await page.keyboard.press('Home');
  for (let k = 0; k < 5; k++) await page.keyboard.press('ArrowRight');
  for (let k = 0; k < 3; k++) await page.keyboard.press('Shift+ArrowRight');
  await espera(500);
  await page.keyboard.type('400', { delay: 250 });
  await espera(1000);
  await page.keyboard.press('Control+Enter');
  marca('re400'); await espera(1500);
  await suave('.jp-Notebook .jp-Cell', iBase, 2500);
  await page.locator('.jp-Notebook .jp-Cell').nth(iBase).locator('.cm-content').click();
  const promptFig = await page.locator('.jp-Notebook .jp-Cell').nth(iBase + 1).locator('.jp-InputPrompt').innerText();
  await page.keyboard.press('Control+Enter');
  await page.locator('.jp-Notebook .jp-Cell').nth(iBase + 1).locator('.cm-content').click();
  await page.keyboard.press('Control+Enter');
  await page.locator('.jp-Notebook .jp-Cell').nth(iBase).locator('.jp-InputPrompt').click();
  marca('corre_400');
  await page.waitForFunction((i) => document.querySelectorAll('.jp-Notebook .jp-Cell')[i].querySelector('.jp-OutputArea').innerText.includes('Re =  400'),
                             iBase, { timeout: 180000 });
  await page.waitForFunction((i) => document.querySelectorAll('.jp-Notebook .jp-Cell')[i].querySelector('.jp-OutputArea').innerText.includes('Reacoplamiento'),
                             iBase, { timeout: 180000 });
  marca('salida_400'); await espera(5000);
  await page.waitForFunction(([i, antes]) => {
      const c = document.querySelectorAll('.jp-Notebook .jp-Cell')[i + 1];
      const pr = c.querySelector('.jp-InputPrompt').innerText;
      return pr !== antes && !pr.includes('*') && c.querySelectorAll('img').length >= 2; },
    [iBase, promptFig], { timeout: 180000 });
  await espera(1500);
  await suave('.jp-Notebook .jp-Cell', iBase + 1, 2500, 40);
  marca('figura_400'); await espera(6000);
  marca('fin');

  const ruta = await page.video().path();
  await context.close(); await browser.close();
  fs.writeFileSync(__dirname + '/eventos.json', JSON.stringify({ video: ruta, eventos }, null, 1));
  console.log('video', ruta);
})();
