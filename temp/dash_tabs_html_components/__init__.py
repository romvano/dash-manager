from __future__ import print_function as _

import os as _os
import sys as _sys

import dash_tabs as _dash_tabs

from .version import __version__

if not hasattr(_dash_tabs, 'development'):
    print("DashTabs was not successfully imported. Make sure you don't have a file "
          "named \n'dash_tabs.py' in your current directory.", file=_sys.stderr)
    _sys.exit(1)

_current_path = _os.path.dirname(_os.path.abspath(__file__))

_components = _dash_tabs.development.component_loader.load_components(
    _os.path.join(_current_path, 'metadata.json'),
    'dash_tabs_html_components'
)

_this_module = _sys.modules[__name__]

_js_dist = [{
    "relative_package_path": "bundle.js",
    "external_url": (
        "https://unpkg.com/dash_tabs-html-components@{}"
        "/dash_tabs_html_components/bundle.js"
    ).format(__version__),
    "namespace": "dash_tabs_html_components"
}]

for component in _components:
    setattr(_this_module, component.__name__, component)
    setattr(component, '_js_dist', _js_dist)
