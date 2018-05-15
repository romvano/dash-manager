import base64
import traceback
from importlib._bootstrap_external import SourceFileLoader

from dash.dependencies import Output, Input
from flask import Flask, send_from_directory, g
from dash import Dash
import os
from os.path import abspath
from urllib.parse import unquote

from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

from layout import *
from utils import get_directory, pip_install

STATIC_PATH = os.path.join(os.path.dirname(abspath(__file__)), 'static')

server = Flask(__name__)
homepage = Dash(__name__, server=server, url_base_pathname='/home')
homepage.css.config.serve_locally = True
homepage.scripts.config.serve_locally = True
homepage.config.supress_callback_exceptions = True
homepage.layout = HOMEPAGE_LAYOUT
dispatcher = DispatcherMiddleware(server)

@homepage.callback(Output(TABS_LIST_ID, 'tabs'), [Input(UPLOAD_ID, 'contents'), Input(UPLOAD_ID, 'filename')])
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None and list_of_names is not None:
        for contents, name in zip(list_of_contents, list_of_names):
            contents = base64.b64decode(contents.split(',')[1])
            if ".py" in name and b"Dash" in contents:
                print('file accepted')
                with open(os.path.join(get_directory(), name), 'wb') as f:
                    f.write(contents)
            else:
                print('file rejected')
    return generate_tab_list()


@homepage.callback(Output(TAB_OUTPUT_ID, 'children'), [Input(TABS_LIST_ID, 'value')])
def render(resource):
    global DEFAULT_CALLBACK_MAP
    if resource is None:
        homepage.callback_map = DEFAULT_CALLBACK_MAP.copy()
        return DEFAULT_LAYOUT
    full_path = os.path.join(get_directory(), unquote(resource))
    with open(full_path) as f:
        if 'Dash' not in f.read():
            return error_layout("Этот файл не содержит объект Dash")
    try:
        dash_module = SourceFileLoader('', full_path).load_module()
    except ImportError as ie:
        pip_install(ie.__str__().split("'")[1])
        return render(resource)
    except:
        error = 'File: ' + (traceback.format_exc().split('File')[-1]).split('/')[-1]
        return error_layout(error)
    finally:
        dash_app = [getattr(dash_module, x) for x in dir(dash_module) if isinstance(getattr(dash_module, x), Dash)][0]
        homepage.callback_map = DEFAULT_CALLBACK_MAP.copy()
        inputs = [[Input(i['id'], i['property']) for i in input_list] for input_list in map(lambda v: v['inputs'], dash_app.callback_map.values())]
        outputs = map(lambda k: Output(*(k.split('.'))), dash_app.callback_map.keys())
        callbacks =  map(lambda v: v['callback'], dash_app.callback_map.values())
        for input, output, callback in zip(inputs, outputs, callbacks):
            homepage.callback(output, input)(callback)
        return dash_app.layout


@server.route('/static/<resource>')
def serve_static(resource):
    return send_from_directory(STATIC_PATH, resource)


DEFAULT_CALLBACK_MAP = homepage.callback_map

if __name__ == '__main__':
    print("Using dashes directory:", get_directory())
    run_simple('localhost', 5000, dispatcher, use_reloader=True, use_debugger=True)