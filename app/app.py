import plotly.graph_objects as go

import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate

from core.experiment import setup_experiment
from core.signal import await_read_signal


DEVICE = setup_experiment()


# --------        spectrum-graph        --------
fig = go.Figure()

fig.add_traces([
    go.Scatter(
        x=[], y=[],
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
], id='read-form')


# --------        app        --------
app = Dash(
    __name__,
    update_title=None,
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
])


# --------        callbacks        --------
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
        signal = await_read_signal(device=DEVICE)

    except AssertionError:
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
