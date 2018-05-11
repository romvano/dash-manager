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

from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

from styles import *

DEFAULT_DIR = abspath("dashes/")
DASHES_LIST_ID = "dashes-list"
TABS_LIST_ID = "tabs"
UPLOAD_ID = "upload-data"
TAB_OUTPUT_ID = "tab-output"
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

def generate_tab_list():
    tab_list = []
    for filename in sorted([f for f in ls(get_directory()) if ".py" in f]):
        tab_list.append({'label': filename, 'value': filename})
    return tab_list


def generate_homepage():
    header = html.Div(
        children=html.H1(
            "DASH",
            style=dash_header_style
        ),
        style=dash_header_div_style
    )
    tabs = dcc.Tabs(
        tabs=generate_tab_list(),
        id=TABS_LIST_ID,
        vertical=True,
        style=dash_tabs_style
    )
    upload = html.Div(
        children=html.Div(
            children=dcc.Upload(
                id=UPLOAD_ID,
                children=html.Div("Добавить файл"),
                multiple=True
            ),
            style=dash_upload_style,
            title="Добавить можно только файлы с расширением .py и использованием объекта Dash"
        ),
        style=dash_upload_div_style
    )
    tabs_div = html.Div(
        children=[header, tabs, upload],
        style=dash_tabs_div_style
    )
    tab_output = html.Div(
        html.Div(id=TAB_OUTPUT_ID),
        style=dash_tab_output_style
    )
    html_list = [
        tabs_div,
        tab_output,
    ]
    return html.Div(children=html_list, style=dash_style)


server = Flask(__name__)
homepage = Dash(__name__, server=server, url_base_pathname='/home')
homepage.css.config.serve_locally = True
homepage.scripts.config.serve_locally = True
homepage.layout = generate_homepage()
dispatcher = DispatcherMiddleware(server)


@homepage.callback(Output(TABS_LIST_ID, 'tabs'), [Input(UPLOAD_ID, 'contents'), Input(UPLOAD_ID, 'filename')])
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None and list_of_names is not None:
        for contents, name in zip(list_of_contents, list_of_names):
            contents = base64.b64decode(contents.split(',')[1])
            if ".py" in name and b"Dash" in contents:
                with open(os.path.join(get_directory(), name), 'wb') as f:
                    f.write(contents)
    return generate_tab_list()


@homepage.callback(Output(TAB_OUTPUT_ID, 'children'), [Input(TABS_LIST_ID, 'value')])
def render(resource):
    p = html.P("Выберите файл слева либо загрузите новый", style=default_p_style)
    upload = html.Div(
        children=dcc.Upload(
            id=UPLOAD_ID,
            children=html.Div("Добавить файл"),
            multiple=True
        ),
        style=default_upload_style,
        title="Добавить можно только файлы с расширением .py и использованием объекта Dash"
    )

    default_layout = html.Div(
        children=[p, upload],
        style=default_div_style
    )

    if resource is None:
        return default_layout
    dash_module = SourceFileLoader('', os.path.join(get_directory(), unquote(resource))).load_module()
    dash_app = [getattr(dash_module, x) for x in dir(dash_module) if isinstance(getattr(dash_module, x), Dash)][0]
    return dash_app.layout


@server.route('/static/<resource>')
def serve_static(resource):
    return send_from_directory(STATIC_PATH, resource)


if __name__ == '__main__':
    print("Using dashes directory:", get_directory())
    run_simple('localhost', 5000, dispatcher, use_reloader=True, use_debugger=True)