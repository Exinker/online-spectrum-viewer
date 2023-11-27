import plotly.graph_objects as go

import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate

from core.config import N_FRAMES, STYLESHEET, GRAPH_BACKGROUND_COLOR, GRAPH_SIGNAL_COLOR
from core.experiment import StatusDeviceError, setup_experiment, is_disconnected
from core.signal import read_signal


DEVICE = setup_experiment()


# --------        spectrum-graph        --------
fig = go.Figure()

fig.add_traces([
    go.Scatter(
        x=[], y=[],
        line={'color': GRAPH_SIGNAL_COLOR, 'width': 1},
    ),
])

fig.layout = go.Layout()
fig.layout.xaxis=dict(
    title=r'number',
    mirror=True,
)
fig.layout.yaxis=dict(
    title=r'I [%]',
    mirror=True,
)
fig.layout.template = 'simple_white'
fig.layout.plot_bgcolor = GRAPH_BACKGROUND_COLOR
fig.layout.paper_bgcolor = GRAPH_BACKGROUND_COLOR

show_signal_graph = dcc.Graph(
    figure=fig,
    mathjax=True,
    id='spectrum-graph',
)


# --------        read-form        --------
read_signal_form = dbc.Form([
    dbc.Button(
        'Read Spectrum',
        color='success', outline=True,
        id='read-spectrum-button',
    ),
    dbc.Checkbox(
        value=False,
        label='real-time',
        id='real-time-checkbox',
    ),
], id='read-form')


# --------        app        --------
app = Dash(
    __name__,
    update_title=None,
    external_stylesheets=[
        STYLESHEET,
    ],
)
app.layout = html.Div([
    html.H1(
        'Online Spectrum Viewer',
        style={
            'text-align': 'center',
            'padding': '20px',
        },
    ),
    dbc.Row([
        read_signal_form,
    ]),
    dbc.Row([
        show_signal_graph,
    ]),
    dcc.Interval(
        interval=1000/N_FRAMES,
        id='timer',
    ),
    html.Div(
        id='empty-div',
        style={'display': 'none'},
    ),
], style={'background-color': GRAPH_BACKGROUND_COLOR})


# --------        callbacks        --------
@app.callback(
    Output('empty-div', 'children'),
    Input('timer', 'n_intervals'),
)
def read_device(n_intervals: int) -> None:
    """Read signal from device by `timer`."""

    try:
        DEVICE.read()

    except StatusDeviceError as error:
        if is_disconnected(DEVICE):
            pass  # TODO: add reconnection!

        raise PreventUpdate

@app.callback(
    Output('read-spectrum-button', 'disabled'),
    Input('real-time-checkbox', 'value'),
)
def set_active_read_button(is_checked: bool) -> bool:
    """Set disabled of `read-spectrum-button` by `real-time-checkbox`."""
    return is_checked


@app.callback(
    Output('read-spectrum-button', 'n_clicks'),
    Input('timer', 'n_intervals'),
    State('read-spectrum-button', 'n_clicks'),
    State('real-time-checkbox', 'value'),
)
def click_read_button(n_intervals: int, n_clicks_read_button: int | None, is_checked_runtime_checkbox: bool) -> bool:
    """Click `read-light-signal-button` by `timer`."""

    if not is_checked_runtime_checkbox:
        raise PreventUpdate

    return 0 if n_clicks_read_button is None else n_clicks_read_button


@app.callback(
    Output('spectrum-graph', 'extendData'),
    Input('read-spectrum-button', 'n_clicks'),
)
def update_signal_graph(n_clicks: int | None):
    """Update graph by click on `Read` button."""
    if n_clicks is None:
        raise PreventUpdate

    # read signal
    try:
        signal = read_signal(storage=DEVICE.storage)

    except AssertionError:
        raise PreventUpdate
    
    if signal is None:
        raise PreventUpdate

    #
    return (
        dict(x=[signal.number], y=[signal.value]),
        [0],
        signal.n_numbers,
    )


if __name__ == '__main__':
    app.run(
        host='0.0.0.0', port=8050,
        debug=True,
    )
