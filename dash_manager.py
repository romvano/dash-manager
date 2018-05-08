import base64
from importlib._bootstrap_external import SourceFileLoader

from dash.dependencies import Output, Input
from flask import Flask, send_from_directory
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import argparse
import os
from os.path import isdir, abspath
from os import listdir as ls, makedirs as mkdir
from urllib.parse import quote, unquote

from werkzeug.routing import Rule
from werkzeug.serving import run_simple
from werkzeug.utils import redirect
from werkzeug.wsgi import DispatcherMiddleware

from styles import *

DEFAULT_DIR = abspath("dashes/")
DASHES_LIST_ID = "dashes-list"
UPLOAD_ID = "upload-data"
STATIC_PATH = os.path.join(os.path.dirname(abspath(__file__)), 'static')

def get_directory():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", type=str, help="sets directory for storing files", default=DEFAULT_DIR)
    args = parser.parse_args()
    if not isdir(args.directory):
        if args.directory == DEFAULT_DIR:
            mkdir(args.directory)
        else:
            print("No such directory: %s" % args.directory)
            exit(0)
    return args.directory

def generate_dashes_list():
    href_list = []
    for filename in [f for f in ls(get_directory()) if ".py" in f]:
        href_list.append(html.Hr())
        href_list.append(html.A(filename, href="dashes/%s" % quote(filename)))
    return href_list

def generate_homepage():
    html_list = [
        html.H1(
            "Dash",
            style=dash_header_style
        ),
        dcc.Upload(
            id=UPLOAD_ID,
            children=html.Div("Добавить файл"),
            style=dash_upload_style,
            multiple=True
        ),
        html.Div(
            "Добавить можно только файлы с расширением .py и использованием объекта Dash",
            style=dash_paragraph_style
        ),
        html.Div(
            generate_dashes_list(),
            id=DASHES_LIST_ID,
            style=dashes_list_style
        )
        # html.Script(
        #     "swal('hi')"
        # ),
    ]
    return html.Div(children=html_list, style=dash_style)


server = Flask(__name__)
homepage = Dash(__name__, server=server, url_base_pathname='/home')
homepage.css.config.serve_locally = True
homepage.scripts.config.serve_locally = True
# homepage.css.append_css({'external_url': "/static/node_modules/sweetalert2/dist/sweetalert2.min.css"})
# homepage.scripts.append_script({'external_url': "/static/node_modules/sweetalert2/dist/sweetalert2.all.min.js"})
# dcc._css_dist[0]['relative_package_path'].append("/static/node_modules/sweetalert2/dist/sweetalert2.min.css")
# dcc._js_dist.append({'relative_package_path': "/static/node_modules/sweetalert2/dist/sweetalert2.all.min.js"})
homepage.layout = generate_homepage()
dispatcher = DispatcherMiddleware(server)


@homepage.callback(Output(DASHES_LIST_ID, 'children'), [Input(UPLOAD_ID, 'contents'), Input(UPLOAD_ID, 'filename')])
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None and list_of_names is not None:
        for contents, name in zip(list_of_contents, list_of_names):
            contents = base64.b64decode(contents.split(',')[1])
            if ".py" in name and b"Dash" in contents:
                with open(os.path.join(get_directory(), name), 'wb') as f:
                    f.write(contents)
    return generate_dashes_list()


@server.route('/static/<resource>')
def serve_static(resource):
    return send_from_directory(STATIC_PATH, resource)


@server.route('/dashes/<path:resource>/')
def render_dash(resource):
    if 'dashes/' + resource not in dispatcher.mounts:
        try:
            dash_module = SourceFileLoader('', os.path.join(get_directory(), unquote(resource))).load_module()
        except FileNotFoundError:
            return redirect('/')
        dash_app = [getattr(dash_module, x) for x in dir(dash_module) if isinstance(getattr(dash_module, x), Dash)][0]
        dash_app.config.requests_pathname_prefix = '/dashes/' + resource + '/render/'
        dash_app.config.routes_pathname_prefix = '/dashes/' + resource + '/render/'
        dash_app.css.config.serve_locally = True
        dash_app.scripts.config.serve_locally = True

        existing_rules = [rule for rule in dash_app.server.url_map.iter_rules()]
        for rule in existing_rules:
            dash_app.server.url_map.add(Rule('/render' + rule.rule, endpoint=rule.endpoint))

        dispatcher.mounts.update({'/dashes/' + resource: dash_app.server.wsgi_app})
    return redirect('/dashes/' + resource + '/render/')

if __name__ == '__main__':
    print("Using dashes directory:", get_directory())
    run_simple('localhost', 5000, dispatcher, use_reloader=True, use_debugger=True)
