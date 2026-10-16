"""
Render the Flask app's Jinja templates as static pages for the GitHub Pages demo.

The templates in prediccion-salarial/app/templates are rendered unchanged; only
the output is adjusted for a static site:
  - url_for() returns relative paths (works under any sub-path);
  - CDN scripts are pinned to fixed versions;
  - the demo scripts and a short notice are added after the header/app.js;
  - the result page is rendered with placeholders (__P:path__) that
    demo/js/demo.js fills in from the prediction stored in localStorage.

The adapted JavaScript (demo/js/app.js, demo/js/demo.js) is maintained by hand.

Usage (from the repository root, with Flask/Jinja2 and Pillow installed):
    python demo/tools/build_pages.py
"""

import re
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / 'prediccion-salarial' / 'app'
DEMO = ROOT / 'demo'

REPO_URL = 'https://github.com/santiagodie/graduate-salary-predictor'

CDN_REPLACEMENTS = {
    '<script src="https://cdn.tailwindcss.com"></script>':
        '<script src="https://cdn.tailwindcss.com/3.4.17"></script>',
    '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>':
        '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js"></script>',
}

PAGES = {
    'views.inicio': 'index.html',
    'views.info': 'info.html',
    'views.formulario': 'formulario.html',
    'views.resultado': 'resultado.html',
    'views.error': 'error.html',
}

NOTICE = (
    '\n    <!-- Static demo notice -->\n'
    '    <div class="bg-blue-50 border-b border-blue-100 text-center text-xs text-blue-800 py-1.5 px-4">\n'
    '        <span data-i18n-html="demo.notice">Demo estática: el modelo se ejecuta en tu navegador. '
    f'La versión completa es una app Flask (<a href="{REPO_URL}" class="underline">ver repositorio</a>).</span>\n'
    '    </div>\n'
)


def statistics_call(var):
    original = (
        "fetch('/api/statistics', {\n"
        "            method: 'POST',\n"
        "            headers: { 'Content-Type': 'application/json' },\n"
        f"            body: JSON.stringify({var})\n"
        "        })"
    )
    return original, f'DemoApi.statistics({var})'


# The result page's inline script calls the Flask API; use the in-browser version
RESULT_REPLACEMENTS = dict([statistics_call('initialFilters'), statistics_call('filters')])


def url_for(endpoint, **values):
    if endpoint == 'static':
        return values['filename']
    return PAGES[endpoint]


class Placeholder:
    """Stands in for the prediction dict; renders as __P:dotted.path__."""

    def __init__(self, path=''):
        self._path = path

    def __getattr__(self, name):
        return Placeholder(f'{self._path}.{name}' if self._path else name)

    __getitem__ = __getattr__

    def __str__(self):
        return f'__P:{self._path}__'

    def __html__(self):
        return str(self)


def tojson(value):
    if isinstance(value, Placeholder):
        return Markup('window.DEMO_PREDICTION')
    raise TypeError('tojson is only expected for the prediction placeholder')


def render(env, template, output, replacements=None, **context):
    html = env.get_template(template).render(**context)
    for old, new in {**CDN_REPLACEMENTS, **(replacements or {})}.items():
        assert html.count(old) == 1, f'{template}: {old}'
        html = html.replace(old, new)

    app_js = '<script src="js/app.js"></script>'
    assert html.count(app_js) == 1
    html = html.replace(app_js, app_js + '\n    <script src="js/demo.js"></script>')

    html = re.sub(r'(</header>\n)', lambda m: m.group(1) + NOTICE, html, count=1)
    html = html.replace('<body class="bg-gray-50">',
                        f'<body class="bg-gray-50" data-page="{output[:-5]}">', 1)
    (DEMO / output).write_text(html, encoding='utf-8', newline='\n')
    print('wrote', output)


def copy_assets():
    (DEMO / 'css').mkdir(exist_ok=True)
    shutil.copyfile(APP / 'static' / 'css' / 'style.css', DEMO / 'css' / 'style.css')

    # The original favicon is an 8000x8000 JPEG (2.7 MB); ship a small copy
    (DEMO / 'img').mkdir(exist_ok=True)
    with Image.open(APP / 'static' / 'img' / 'favicon.jpg') as img:
        img.convert('RGB').resize((64, 64), Image.LANCZOS).save(
            DEMO / 'img' / 'favicon.jpg', quality=90)


def main():
    env = Environment(loader=FileSystemLoader(APP / 'templates'),
                      autoescape=select_autoescape(['html']))
    env.globals['url_for'] = url_for
    env.filters['tojson'] = tojson

    render(env, 'inicio.html', 'index.html')
    render(env, 'info.html', 'info.html', model_info={})
    render(env, 'formulario.html', 'formulario.html', form_id='new')
    render(env, 'resultado.html', 'resultado.html', RESULT_REPLACEMENTS,
           prediction=Placeholder())
    # The only error the static demo can reach: a result id that is not stored
    render(env, 'error.html', 'error.html',
           error_code='not_found', error_message='Predicción no encontrada')
    copy_assets()


if __name__ == '__main__':
    main()
