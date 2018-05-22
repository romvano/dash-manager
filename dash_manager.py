import base64
import traceback
from importlib._bootstrap_external import SourceFileLoader
from urllib.parse import unquote, urlencode, urlparse, parse_qsl

from dash.dependencies import Output, Input, State
from flask import Flask, send_from_directory
from dash import Dash
import os
from os.path import abspath

import json
from werkzeug.routing import Rule, Map
from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

from layout import *
from upload_rewrite import get_upload_dash
from utils import get_directory, pip_install, write_file

STATIC_PATH = os.path.join(os.path.dirname(abspath(__file__)), 'static')
DASH_UPLOAD_RESULTS_FLAG = 'dash_manager_upload_results_flag'
UPLOAD_RESULT_URL_PART = "dash-manager_upload-results_unique-name"
TAB_SWITCH_MESSAGE = "dash-manager:goto_tab/"

INTERVAL_IN_MS = 10 * 1000

server = Flask(__name__)
homepage = Dash(__name__, server=server, url_base_pathname='/')
homepage.css.config.serve_locally = True
homepage.scripts.config.serve_locally = True
homepage.config.supress_callback_exceptions = True
homepage.layout = HOMEPAGE_LAYOUT
dispatcher = DispatcherMiddleware(server)


@homepage.callback(Output(TABS_LIST_ID, 'tabs'), [Input(INVISIBLE_ID, 'children')])
def update_tab_list(content):
    homepage.layout[INVISIBLE_ID].children = content
    return generate_tab_list()


@homepage.callback(Output(INTERVAL_DATA_DIV_ID, 'children'), [Input(INTERVAL_ID, 'n_intervals')])
def pass_intervals_to_callback(n):
    return n


@homepage.callback(Output(TABS_LIST_ID, 'value'), [Input(INVISIBLE_ID, 'children'), Input(INTERVAL_DATA_DIV_ID, 'children'), Input(LOCATION_ID, 'href')])
def pass_callback_to_output(content, n, href):
    if content is not None:
        homepage.layout[INVISIBLE_ID].children = content
        return DASH_UPLOAD_RESULTS_FLAG
    tabs = generate_tab_list()
    if n is not None:
        return tabs[int(n) % len(tabs)]['value']
    if href is not None:
        tab = dict(parse_qsl(urlparse(href).query)).get('tab')
        if tab is not None and tab in [i['value'] for i in tabs]:
            return tab
    return None


@homepage.callback(Output(INVISIBLE_ID, 'children'), [Input(UPLOAD_ID, 'contents')], state=[State(UPLOAD_ID, 'filename')])
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None and list_of_names is not None:
        success, duplicates, wrong_format = [], {}, []
        for contents, name in zip(list_of_contents, list_of_names):
            contents = base64.b64decode(contents.split(',')[1])
            if ".py" in name and b"Dash" in contents:
                if write_file(name, contents, override=False):
                    success.append(name)
                else:
                    duplicates[name] = str(contents, encoding='utf-8')
            else:
                wrong_format.append(name)
        return json.dumps([success, duplicates, wrong_format])
    return None


@homepage.callback(Output(UPLOAD_ID, 'contents'), [Input(DEFAULT_UPLOAD_ID, 'contents')])
def pass_callback_to_upload_contents(contents):
    return contents


@homepage.callback(Output(UPLOAD_ID, 'filename'), [Input(DEFAULT_UPLOAD_ID, 'filename')])
def pass_callback_to_upload_filename(filename):
    return filename


def add_dash(dash_module, resource):
    if not isinstance(dash_module, Dash):
        dash_app = [getattr(dash_module, x) for x in dir(dash_module) if isinstance(getattr(dash_module, x), Dash)][0]
    else:
        dash_app = dash_module
    dash_app.config.requests_pathname_prefix = '/dashes/' + resource + '/render/'
    dash_app.config.routes_pathname_prefix = '/dashes/' + resource + '/render/'
    dash_app.css.config.serve_locally = True
    dash_app.scripts.config.serve_locally = True
    dash_app.server.before_request(lambda: os.chdir(os.path.join(get_directory(), resource) if resource != UPLOAD_RESULT_URL_PART else os.path.join(get_directory(), '..')))
    existing_rules = dash_app.server.url_map.iter_rules()
    dash_app.server.url_map = Map()
    for rule in existing_rules:
        dash_app.server.url_map.add(Rule('/render' + rule.rule.split('render')[-1], endpoint=rule.endpoint))
    dispatcher.mounts.update({'/dashes/' + resource: dash_app.server.wsgi_app})
    return '/dashes/' + resource + '/render/'


@homepage.callback(Output(TAB_OUTPUT_ID, 'children'), [Input(TABS_LIST_ID, 'value')])
def render(resource):
     if resource is None:
         return DEFAULT_LAYOUT
     if resource == DASH_UPLOAD_RESULTS_FLAG:
         loads = json.loads(str(homepage.layout[INVISIBLE_ID].children))
         return render_layout(add_dash(get_upload_dash(*loads), UPLOAD_RESULT_URL_PART))
     dir_path = os.path.join(get_directory(), unquote(resource))
     full_path = os.path.join(dir_path, unquote(resource) + ".py")
     with open(full_path) as f:
         if 'Dash' not in f.read():
             return error_layout("Этот файл не содержит объект Dash")
     try:
         dash_module = SourceFileLoader(resource[:-3], full_path).load_module()
     except ImportError as ie:
         return render(resource) if pip_install(ie.__str__().split("'")[1]) == 0 else error_layout("Невозможно загрузить зависимости")
     except:
         error = traceback.format_exc().split("call_with_frames_removed\n", 1)[1].replace(get_directory() + "/", "")
         return error_layout(error)
     else:
         return render_layout(add_dash(dash_module, resource))


@homepage.callback(Output(INTERVAL_DIV_ID, 'children'), [Input(SLIDESHOW_BUTTON_ID, 'children')])
def turn_interval(btn_state):
    if btn_state == START_SLIDESHOW:
        return None
    return dcc.Interval(
        id=INTERVAL_ID,
        interval=INTERVAL_IN_MS,
        n_intervals=0
    )


@homepage.callback(Output(SLIDESHOW_BUTTON_ID, 'style'), [Input(SLIDESHOW_BUTTON_ID, 'children')])
def change_slideshow_button_bgcolor(btn_state):
    if btn_state == START_SLIDESHOW:
        return dash_slideshow_button_style
    return  dash_slideshow_button_style_red


@homepage.callback(Output(SLIDESHOW_BUTTON_ID, 'children'),
                   [Input(SLIDESHOW_BUTTON_ID, 'n_clicks_timestamp'),
                    Input(TABS_DIV_ID, 'n_clicks_timestamp')],
                   state=[State(SLIDESHOW_BUTTON_ID, 'children')])
def change_slideshow_btn_text(btn_ts, div_ts, btn_state):
    if btn_ts is not None and div_ts is not None and btn_ts >= div_ts - 200 and btn_state == START_SLIDESHOW:
        return STOP_SLIDESHOW
    return START_SLIDESHOW


@homepage.callback(Output(LOCATION_ID, 'search'), [Input(TABS_LIST_ID, 'value')])
def change_url(value):
    if value is None:
        return ""
    state = urlencode({'tab': value})
    return f'?{state}'


@server.route('/static/<resource>')
def serve_static(resource):
    return send_from_directory(STATIC_PATH, resource)


if __name__ == '__main__':
    print("Using dashes directory:", get_directory())
    run_simple('localhost', 5000, dispatcher, use_reloader=True, use_debugger=True, threaded=True)