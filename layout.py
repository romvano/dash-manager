from os import listdir as ls
import dash_core_components as dcc
import dash_html_components as html
from styles import *
from utils import get_directory

DASHES_LIST_ID = "dash-manager__dashes-list"
TABS_LIST_ID = "dash-manager__tabs"
UPLOAD_ID = "dash-manager__upload-data"
TAB_OUTPUT_ID = "dash-manager__tab-output"


def generate_tab_list():
    tab_list = []
    for filename in sorted([f for f in ls(get_directory()) if ".py" in f]):
        tab_list.append({'label': filename, 'value': filename})
    return tab_list


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

default_upload = html.Div(
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
    children=[header, tabs, default_upload],
    style=dash_tabs_div_style
)

tab_output = html.Div(
    html.Div(id=TAB_OUTPUT_ID),
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

default_p = html.P(
    "Выберите файл слева либо загрузите новый",
    style=default_p_style
)

default_upload = html.Div(
    children=dcc.Upload(
        id=UPLOAD_ID,
        children=html.Div("Добавить файл"),
        multiple=True
    ),
    style=default_upload_style,
    title="Добавить можно только файлы с расширением .py и использованием объекта Dash"
)

def error_layout(trace):
    return html.Div(
        children=[html.Div(html.H2("Ошибка исполнения!")), html.Div(html.Pre(trace))],
        style=default_div_style
    )


HOMEPAGE_LAYOUT = html.Div(children=html_list, style=dash_style)
DEFAULT_LAYOUT = html.Div(children=[default_p, default_upload], style=default_div_style)
