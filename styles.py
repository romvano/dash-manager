WIDTH = 98
HEIGHT = 98
TABS_WIDTH = 0.2 * WIDTH
CONTENT_WIDTH = WIDTH - TABS_WIDTH
CONTENT_HEIGHT = 1 * HEIGHT
UPLOAD_WIDTH = 90
UPLOAD_HEIGHT = 0.05 * HEIGHT
HEADER_HEIGHT = 0.05 * HEIGHT
TABS_HEIGHT = HEIGHT - HEADER_HEIGHT - 2 * UPLOAD_HEIGHT


dash_style = {
    'width': '%fvw' % WIDTH,
    'height': '%fvh' % HEIGHT,
    'margin': 'auto',
    'min-width': '900px',
    'fontFamily': 'Sans-Serif',
}

dash_slideshow_button_style = {
    'width': '%f%%' % UPLOAD_WIDTH,
    'height': '%fvh' % (UPLOAD_HEIGHT),
    'min-height': '30px',
    'float': 'center',
    'textAlign': 'center',
    'margin-top': '3px',
    'margin-left': '5%',
    'background-color': 'green',
    'color': 'white',
    'font-size': 18,
    'borderRadius': '5px',
    'border': 0,
}

dash_upload_style = {
    'width': '%f%%' % UPLOAD_WIDTH,
    'height': '%fvh' % (UPLOAD_HEIGHT),
    'min-height': '30px',
    'float': 'center',
    'lineHeight': '%fvh' % (UPLOAD_HEIGHT),
    'borderWidth': '1px',
    'borderStyle': 'dashed',
    'borderRadius': '5px',
    'textAlign': 'center',
    'margin': 'auto',
    'margin-top': '3px',
}

dash_upload_div_style = {
    'width': '100%',
    'border-right-color': 'rgb(211, 211, 211)',
    'border-right-style': 'solid',
    'border-right-width': '1px',
    'box-sizing': 'border-box',
}

dash_tabs_style = {
    'height': '%fvh' % TABS_HEIGHT,
    'borderRight': 'thin lightgrey solid',
    'textAlign': 'left',
    'word-wrap': 'break-word',
    'padding-left': '5px',
    'overflow-y': 'auto',
    'overflow-x': 'hidden',
}

dash_tabs_div_style = {
    'width': '%fvw' % TABS_WIDTH,
    'height': '%fvh' % CONTENT_HEIGHT,
    'float': 'left',
}

dash_tab_output_style = {
    'width': '%fvw' % (CONTENT_WIDTH - 1),
    'margin-left': '1vw',
    'height': '%fvh' % CONTENT_HEIGHT,
    'float': 'right',
}

dash_header_div_style = {
    'height': '%fvh' % (HEADER_HEIGHT),
    'min-height': '34px',
    'margin-top': '0px',
    'margin-bottom': '0px',
}

dash_header_style = {
    'margin': '0',
    'padding-left': '5px',
}

default_p_style = {
    'width': '100%',
    'textAlign': 'center',
}

default_upload_style = dash_upload_style.copy()
default_upload_style.update({
    'width': '50%',
    'textAlign': 'center',
    'margin': 'auto',
})

default_div_style = {
    'width': '100%',
    'textAlign': 'center',
    'padding-top': '%fvh' % (CONTENT_HEIGHT // 3),
}

iframe_style = {
    'border': '0px',
    'width': '%fvw' % CONTENT_WIDTH,
    'height': '%fvh' % CONTENT_HEIGHT,
}

invisible_style = {
    'display': 'none',
}