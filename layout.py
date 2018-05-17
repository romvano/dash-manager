from os import listdir as ls

import dash_core_components as dcc
import dash_html_components as html
from styles import *
from utils import get_directory

TABS_DIV_ID = "dash-manager__tabs-div"
TABS_LIST_ID = "dash-manager__tabs"
DEFAULT_UPLOAD_ID = "dash-manager__default__upload"
UPLOAD_ID = "dash-manager__upload-data"
TAB_OUTPUT_ID = "dash-manager__tab-output"
IFRAME_ID = "dash-manager__iframe"
INVISIBLE_ID = "dash-manager__tabs__invisible"
BUTTON_ID = "dash-manager__rewrite-button__%s"
SPAN_ID = "dash-manager__span__%s"

UPLOAD_DESCRIPTION = "Добавить можно только файлы с расширением .py и использованием объекта Dash"


def generate_tab_list():
    tab_list = []
    for filename in sorted([f for f in ls(get_directory()) if ".py" in f]):
        tab_list.append({'label': filename, 'value': filename})
    return tab_list


default_p = html.P(
    "Выберите файл слева либо загрузите новый",
    style=default_p_style
)

default_upload = html.Div(
    children=dcc.Upload(
        id=DEFAULT_UPLOAD_ID,
        children=html.Div("Добавить файл"),
        multiple=True
    ),
    style=default_upload_style,
    title=UPLOAD_DESCRIPTION
)

DEFAULT_LAYOUT = html.Div(children=[default_p, default_upload], style=default_div_style)


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

invisible_div = html.Div(
    id=INVISIBLE_ID,
    style=invisible_style
)

tabs_div = html.Div(
    id=TABS_DIV_ID,
    children=[header, tabs, upload, invisible_div],
    style=dash_tabs_div_style
)

tab_output = html.Div(
    html.Div(id=TAB_OUTPUT_ID, children=DEFAULT_LAYOUT),
    style=dash_tab_output_style
)

swal = html.Div(children=[
    html.Link(href='/static/node_modules/sweetalert2/dist/sweetalert2.min.css', rel="stylesheet"),
    html.Script(src='static/node_modules/sweetalert2/dist/sweetalert2.min.js'),
])

html_list = [
    tabs_div,
    tab_output,
    swal,
]

def error_layout(trace):
    return html.Div(
        children=[html.Div(html.H2("Ошибка исполнения!")), html.Div(html.Pre(trace))],
        style=default_div_style
    )

def render_layout(resource):
    return html.Iframe(src=resource, style=iframe_style)


def upload_result_layout(success, duplicates, wrong_format):
    if not success and not duplicates and not wrong_format:
        return DEFAULT_LAYOUT
    added_files_list = []
    if success:
        added_files_list.append(html.H1("Успешно добавлены файлы:"))
        added_files_list.extend([html.P(name) for name in success])
    if duplicates:
        added_files_list.append(html.H2("Эти файлы уже существуют:"))
        added_files_list.extend([html.P([
            html.Span(name, id=SPAN_ID % i),
            "\t",
            html.Button(children="Перезаписать", id=BUTTON_ID % i)
        ]) for i, name in enumerate(duplicates)])
    if wrong_format:
        added_files_list.append(html.H2("Неверный формат файлов:", title=UPLOAD_DESCRIPTION))
        added_files_list.extend([html.P(name, title=UPLOAD_DESCRIPTION) for name in wrong_format])
    return html.Div(
        children=added_files_list,
        style=default_div_style
    )


HOMEPAGE_LAYOUT = html.Div(children=html_list, style=dash_style)
