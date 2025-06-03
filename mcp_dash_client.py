import dash
from dash import html, dcc, Output, Input, State, ctx, MATCH, ALL
import dash_bootstrap_components as dbc
import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
import nest_asyncio
from databricks.sdk.core import Config

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)
config = Config()
token = config.oauth_token().access_token
headers = {"Authorization": f"Bearer {token}"}
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
        html, body {
            background: #fff !important;
            color: #111 !important;
            font-family: 'Inter', 'Segoe UI', system-ui, Arial, sans-serif;
            font-size: 15px;
            letter-spacing: 0.01em;
        }
        .container, .row, .col, .card, .navbar, .footer, .alert, .card-body, .card-header, .card-footer {
            background: #fff !important;
            color: #111 !important;
            border-color: #e0e0e0 !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        }
        .card, .card-body, .card-header, .card-footer {
            margin-bottom: 18px !important;
            padding: 18px 22px !important;
        }
        .navbar, .footer {
            border-radius: 0 !important;
            box-shadow: none !important;
            border-bottom: 1px solid #e0e0e0 !important;
        }
        hr {
            border-top: 1px solid #e0e0e0 !important;
        }
        .btn, .btn-primary, .btn-success, .btn-info, .btn-secondary {
            background: #fff !important;
            color: #111 !important;
            border: 1.5px solid #111 !important;
            border-radius: 6px !important;
            font-weight: 500;
            padding: 8px 22px !important;
            transition: background 0.2s, color 0.2s, border 0.2s;
            box-shadow: none !important;
        }
        .btn:hover, .btn:focus, .btn:active {
            background: #f7f7f7 !important;
            color: #000 !important;
            border: 1.5px solid #000 !important;
        }
        input, .form-control {
            background: #fff !important;
            color: #111 !important;
            border: 1.5px solid #e0e0e0 !important;
            border-radius: 6px !important;
            box-shadow: none !important;
            padding: 8px 12px !important;
            font-size: 15px !important;
            transition: border 0.2s;
        }
        input:focus, .form-control:focus {
            border: 1.5px solid #111 !important;
            outline: none !important;
            background: #fafafa !important;
        }
        .alert-success, .alert-danger, .alert-warning, .alert-info {
            background: #fafafa !important;
            color: #111 !important;
            border: 1.5px solid #e0e0e0 !important;
            border-radius: 6px !important;
        }
        label, .form-label {
            color: #222 !important;
            font-weight: 500 !important;
            margin-bottom: 6px !important;
            letter-spacing: 0.01em;
        }
        a, a:visited, a:hover, a:active {
            color: #111 !important;
            text-decoration: underline;
            transition: color 0.2s;
        }
        ::-webkit-input-placeholder { color: #aaa !important; }
        ::-moz-placeholder { color: #aaa !important; }
        :-ms-input-placeholder { color: #aaa !important; }
        ::placeholder { color: #aaa !important; }
        * {
            box-shadow: none !important;
        }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Helper to run async code in sync Dash callbacks
nest_asyncio.apply()
def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

# Remove global client
# client = None

def create_client(url, token):
    transport = StreamableHttpTransport(
        url=url,
        headers={"Authorization": f"Bearer {token}"}
    )
    return Client(transport)

def list_tools(url, token):
    try:
        client = create_client(url, token)
        async def _list():
            async with client:
                return await client.list_tools()
        tools = run_async(_list())
        def serialize(obj):
            if hasattr(obj, "dict"):
                return obj.dict()
            elif hasattr(obj, "__dict__"):
                return obj.__dict__
            else:
                return str(obj)
        return [serialize(t) for t in tools]
    except Exception as e:
        return []

def call_tool(name, arguments, url, token):
    try:
        client = create_client(url, token)
        async def _call():
            async with client:
                return await client.call_tool(name=name, arguments=arguments)
        result = run_async(_call())
        # Only return the final text field (assume result is a list of TextContent)
        if isinstance(result, list) and result and hasattr(result[0], 'text'):
            return result[0].text
        elif isinstance(result, list) and result and isinstance(result[0], dict) and 'text' in result[0]:
            return result[0]['text']
        else:
            return str(result)
    except Exception as e:
        return f"Error: {e}"

# Dash app
app.layout = dbc.Container([
    # Minimalist top bar with title
    html.Div(
        'MCP Client',
        style={
            'width': '100%',
            'background': '#fff',
            'color': '#111',
            'fontWeight': 'bold',
            'fontSize': '2rem',
            'textAlign': 'center',
            'padding': '18px 0 10px 0',
            'borderBottom': '2px solid #e0e0e0',
            'letterSpacing': '0.04em',
            'marginBottom': '0',
            'zIndex': 1000
        }
    ),
    dbc.NavbarSimple(
        brand="MCP Dash Client",
        color="primary",
        dark=True,
        className="mb-4"
    ),
    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("MCP URL"),
                    dbc.Input(id="url", value="", type="text"),
                ], md=6),
                dbc.Col([
                    dbc.Label("Token"),
                    dbc.Input(id="token", value=headers['Authorization'].split(' ')[1], type="password"),
                ], md=4),
                dbc.Col([
                    dbc.Button("Connect", id="connect-btn", color="success", className="mt-4 w-100"),
                ], md=2),
            ], className="mb-2"),
            html.Div(id="connect-status", className="mb-2"),
        ])
    ], className="mb-4 shadow-sm"),
    dbc.Row([
        # Sidebar: tool list
        dbc.Col([
            dbc.Button("List Tools", id="list-tools-btn", color="info", className="mb-2 w-100"),
            html.Div(id="tool-list"),
        ], md=3),
        # Main area: tool input and result
        dbc.Col([
            html.Div(id="tool-input-form"),
            dcc.Loading(
                id="loading-tool-call",
                type="circle",
                color="#111",
                children=html.Div(id="tool-call-result", className="mt-3")
            ),
        ], md=9),
    ]),
    dcc.Markdown(
        """
        <style>
        body, .container, .row, .col, .card, .navbar, .footer, .alert, .card-body, .card-header, .card-footer {
            background: #fff !important;
            color: #000 !important;
            border-color: #e0e0e0 !important;
            box-shadow: none !important;
        }
        .btn, .btn-primary, .btn-success, .btn-info, .btn-secondary {
            background: #fff !important;
            color: #000 !important;
            border: 1px solid #000 !important;
            border-radius: 0 !important;
            font-weight: 500;
            transition: background 0.2s, color 0.2s;
        }
        .btn:hover, .btn:focus, .btn:active {
            background: #000 !important;
            color: #fff !important;
        }
        input, .form-control {
            background: #fff !important;
            color: #000 !important;
            border: 1px solid #e0e0e0 !important;
            border-radius: 0 !important;
            box-shadow: none !important;
        }
        input:focus, .form-control:focus {
            border: 1.5px solid #000 !important;
            outline: none !important;
        }
        .alert-success, .alert-danger, .alert-warning, .alert-info {
            background: #fff !important;
            color: #000 !important;
            border: 1px solid #000 !important;
        }
        hr {
            border-top: 1px solid #e0e0e0 !important;
        }
        a, a:visited, a:hover, a:active {
            color: #000 !important;
            text-decoration: underline;
        }
        label, .form-label {
            color: #000 !important;
            font-weight: 500 !important;
        }
        * {
            box-shadow: none !important;
        }
        </style>
        """,
        dangerously_allow_html=True
    ),
    dcc.Store(id="tools-store"),
    dcc.Store(id="selected-tool-store"),
    dcc.Store(id="connection-store")
], fluid=True, style={"backgroundColor": "#fff", "minHeight": "100vh"})

# Update connect callback to store connection info
@app.callback(
    Output("connect-status", "children"),
    Output("connection-store", "data"),
    Input("connect-btn", "n_clicks"),
    State("url", "value"),
    State("token", "value"),
    prevent_initial_call=True
)
def connect(n, url, token):
    if not url or not token:
        return "Please provide both URL and token.", dash.no_update
    try:
        # Test connection by listing tools
        _ = list_tools(url, token)
        return dbc.Alert("Connected!", color="success"), {"url": url, "token": token}
    except Exception as e:
        return dbc.Alert(f"Connection failed: {e}", color="danger"), dash.no_update

@app.callback(
    Output("tools-store", "data"),
    Output("tool-list", "children"),
    Input("list-tools-btn", "n_clicks"),
    State("connection-store", "data"),
    prevent_initial_call=True
)
def list_tools_callback(n, conn):
    if not conn:
        return [], dbc.Alert("Not connected.", color="warning")
    tools = list_tools(conn["url"], conn["token"])
    if not tools:
        return [], dbc.Alert("No tools found or not connected.", color="warning")
    # List as buttons
    btns = [
        dbc.Button(tool['name'], id={'type': 'tool-btn', 'index': i}, color="secondary", outline=True, className="mb-2 w-100")
        for i, tool in enumerate(tools)
    ]
    return tools, btns

@app.callback(
    Output("selected-tool-store", "data"),
    Input({'type': 'tool-btn', 'index': ALL}, 'n_clicks'),
    State("tools-store", "data"),
    prevent_initial_call=True
)
def select_tool(n_clicks, tools):
    if not tools or not n_clicks:
        return dash.no_update
    for i, n in enumerate(n_clicks):
        if n:
            return tools[i]
    return dash.no_update

@app.callback(
    Output("tool-input-form", "children"),
    Input("selected-tool-store", "data"),
    prevent_initial_call=True
)
def render_tool_input_form(tool):
    if not tool:
        return ""
    # Dynamically render input fields based on tool inputSchema
    schema = tool.get('inputSchema', {})
    props = schema.get('properties', {})
    required = schema.get('required', [])
    inputs = []
    for k, v in props.items():
        label = v.get('description', k)
        typ = v.get('type', 'string')
        input_type = 'number' if typ == 'number' else 'text'
        inputs.append(
            html.Div([
                dbc.Label(label),
                dbc.Input(id={'type': 'tool-input', 'key': k}, type=input_type, required=(k in required)),
            ], className="mb-2")
        )
    return dbc.Form([
        html.H5(f"Call Tool: {tool['name']}", className="mb-3"),
        *inputs,
        dbc.Button("Call Tool", id="call-tool-btn", color="primary", className="mt-2"),
    ])

@app.callback(
    Output("tool-call-result", "children"),
    Input("call-tool-btn", "n_clicks"),
    State("selected-tool-store", "data"),
    State({'type': 'tool-input', 'key': ALL}, 'value'),
    State({'type': 'tool-input', 'key': ALL}, 'id'),
    State("connection-store", "data"),
    prevent_initial_call=True
)
def call_tool_callback(n, tool, values, ids, conn):
    if not tool or not n or not conn:
        return ""
    # Build arguments dict
    args = {id['key']: val for id, val in zip(ids, values)}
    result = call_tool(tool['name'], args, conn["url"], conn["token"])
    return dbc.Card([
        dbc.CardBody([
            html.H6("Result", className="mb-2"),
            html.Pre(result, style={"backgroundColor": "#f8f9fa", "padding": "1em"}),
        ])
    ], className="shadow-sm")

if __name__ == "__main__":
    app.run_server(debug=True) 