import dash

from layout import upload_result_layout, BUTTON_ID, SPAN_ID
from dash.dependencies import Output, Input, State

from utils import write_file


def get_upload_dash(success, duplicates, wrong_format):
    d = dash.Dash()
    d.css.config.serve_locally = True
    d.scripts.config.serve_locally = True
    d.config.supress_callback_exceptions = True
    d.layout = upload_result_layout(success, duplicates, wrong_format)

    for i, name in enumerate(duplicates):
        @d.callback(Output(BUTTON_ID % i, 'children'), inputs=[Input(BUTTON_ID % i, 'n_clicks')], state=[State(SPAN_ID % i, 'children')])
        def overwrite_file_on_btn_press(n_clicks, filename):
            if not n_clicks:
                return "Перезаписать файл"
            if n_clicks == 1:
                write_file(filename, bytes(duplicates[name], encoding='utf-8'), override=True)
                return "Сохранено"
            return "Сохранено"

    return d
