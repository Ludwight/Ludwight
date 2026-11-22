"""Genera reporte.pdf: Markdown -> HTML (pandoc, ecuaciones en MathML) -> PDF (Chromium vía Playwright)."""
import subprocess
from pathlib import Path

here = Path(__file__).resolve().parent
html = here / "reporte.html"
subprocess.run(["pandoc", str(here / "reporte.md"), "-s", "--mathml",
                "--css", "estilo.css", "-o", str(html)], check=True)
# Chromium (Playwright para Node, preinstalado) imprime el HTML a PDF
js = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('{html.as_uri()}'); await p.waitForLoadState('networkidle');
  await p.pdf({{ path: '{here / "reporte.pdf"}', format: 'Letter', printBackground: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-size:8pt;width:100%;text-align:center;color:#666"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',
    margin: {{ top: '16mm', bottom: '18mm', left: '17mm', right: '17mm' }} }});
  await b.close();
}})();
"""
subprocess.run(["node", "-e", js], check=True)
html.unlink()
print("reporte.pdf listo")
