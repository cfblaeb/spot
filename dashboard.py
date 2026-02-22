import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
import sqlite3
from datetime import datetime, timedelta

# Initialiser Dash-appen
app = dash.Dash(__name__)
app.title = "BME680 Dashboard"
DB_FILE = "airquality.db"

# --- Hjælpefunktion til at bygge traffiklyset (HTML) ---
def get_traffic_light(accuracy):
    if accuracy is None:
        color, text = '#cccccc', 'Ingen data'
    elif accuracy == 3:
        color, text = '#00cc66', 'Nøjagtig (3/3)'  # Grøn
    elif accuracy == 2:
        color, text = '#ffcc00', 'Kalibrerer (2/3)' # Gul
    else:
        color, text = '#ff4b4b', 'Ustabil (0-1/3)' # Rød

    return html.Div([
        # Selve lys-cirklen
        html.Div(style={
            'backgroundColor': color,
            'height': '40px', 'width': '40px',
            'borderRadius': '50%',
            'margin': '0 auto',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
            'border': '2px solid #fff'
        }),
        # Teksten under lyset
        html.Div(text, style={'marginTop': '10px', 'fontSize': '13px', 'fontWeight': 'bold', 'color': '#555'})
    ])

# --- Frontend Layout ---
app.layout = html.Div(style={'fontFamily': 'sans-serif', 'maxWidth': '1000px', 'margin': '0 auto', 'padding': '20px'}, children=[
    
    html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'textAlign': 'center', 'marginBottom': '20px'}, children=[
        html.H1("🌬️ Indeklima DRAMA"),
        html.Label("Vælg tidsperiode: ", style={'fontSize': '18px', 'marginRight': '10px'}),
        dcc.Dropdown(
            id='time-dropdown',
            options=[
                {'label': 'Seneste 24 timer', 'value': 1},
                {'label': 'Seneste 7 dage', 'value': 7},
                {'label': 'Seneste måned', 'value': 30},
                {'label': 'Længere', 'value': 9999}
            ],
            value=30,
            clearable=False,
            style={'width': '200px', 'display': 'inline-block', 'textAlign': 'left'}
        )
    ]),

    # --- IAQ Container (Graf + Traffiklys) ---
    html.Div(style={'display': 'flex', 'alignItems': 'center', 'backgroundColor': 'white', 'marginBottom': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
        html.Div(dcc.Graph(id='iaq-graph'), style={'flex': '1'}),
        html.Div(id='iaq-traffic-light', style={'width': '120px', 'textAlign': 'center', 'padding': '20px'})
    ]),

    # --- eCO2 Container (Graf + Traffiklys) ---
    html.Div(style={'display': 'flex', 'alignItems': 'center', 'backgroundColor': 'white', 'marginBottom': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
        html.Div(dcc.Graph(id='eco2-graph'), style={'flex': '1'}),
        html.Div(id='eco2-traffic-light', style={'width': '120px', 'textAlign': 'center', 'padding': '20px'})
    ]),

    # Temp, fugt og tryk
    html.Div(dcc.Graph(id='temp-hum-graph'), style={'backgroundColor': 'white', 'marginBottom': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
    html.Div(dcc.Graph(id='hum-graph'), style={'backgroundColor': 'white', 'marginBottom': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
    html.Div(dcc.Graph(id='pressure-graph'), style={'backgroundColor': 'white', 'marginBottom': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
])

# --- Backend Logik ---
@app.callback(
    [Output('iaq-graph', 'figure'),
     Output('eco2-graph', 'figure'),
     Output('temp-graph', 'figure'),
     Output('hum-graph', 'figure'),
     Output('pressure-graph', 'figure'),
     Output('iaq-traffic-light', 'children'),
     Output('eco2-traffic-light', 'children')],
    [Input('time-dropdown', 'value')]
)
def update_graphs(days):
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    conn = sqlite3.connect(DB_FILE)
    # HUSK AT HENTE 'accuracy' FRA DATABASEN!
    query = "SELECT timestamp, temperature, humidity, pressure, iaq, eco2, accuracy FROM sensor_data WHERE timestamp >= ? ORDER BY timestamp ASC"
    df = pd.read_sql_query(query, conn, params=(cutoff_date.strftime('%Y-%m-%d %H:%M:%S'),))
    conn.close()

    if df.empty:
        empty_light = get_traffic_light(None)
        return go.Figure(), go.Figure(), go.Figure(), go.Figure(), empty_light, empty_light

    # Ret tidszonen til dansk tid
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert('Europe/Copenhagen')

    # Aflæs den allernyeste accuracy-værdi til traffiklyset
    latest_accuracy = df['accuracy'].iloc[-1]
    traffic_light_html = get_traffic_light(latest_accuracy)

    # 1. IAQ Graf
    fig_iaq = go.Figure(go.Scatter(x=df['timestamp'], y=df['iaq'], mode='lines', name='IAQ', line=dict(color='#ff4b4b'), fill='tozeroy'))
    fig_iaq.update_layout(title='Indendørs Luftkvalitet (IAQ)', margin=dict(l=20, r=20, t=40, b=20), template='plotly_white')

    # 2. eCO2 Graf
    fig_eco2 = go.Figure(go.Scatter(x=df['timestamp'], y=df['eco2'], mode='lines', name='eCO2 (ppm)', line=dict(color='#00cc66'), fill='tozeroy'))
    fig_eco2.update_layout(title='Estimeret CO2 (ppm)', margin=dict(l=20, r=20, t=40, b=20), template='plotly_white')

    # 3. Temperatur og Fugtighed
    fig_temp = go.Figure(go.Scatter(x=df['timestamp'], y=df['temperature'], mode='lines', name='Temp (°C)', line=dict(color='#ff9f36'), fill='tozeroy'))
    fig_temp.update_layout(title='Temperatur (°C)', margin=dict(l=20, r=20, t=40, b=20), template='plotly_white')

    fig_hum = go.Figure(go.Scatter(x=df['timestamp'], y=df['humidity'], mode='lines', name='Fugtighed (%)', line=dict(color='#1f77b4'), fill='tozeroy'))
    fig_hum.update_layout(title='Fugtighed (%)', margin=dict(l=20, r=20, t=40, b=20), template='plotly_white')

    # 4. Tryk Graf
    fig_pressure = go.Figure(go.Scatter(x=df['timestamp'], y=df['pressure'], mode='lines', name='Tryk (hPa)', line=dict(color='#8c564b'), fill='tozeroy'))
    fig_pressure.update_layout(title='Atmosfærisk Tryk (hPa)', margin=dict(l=20, r=20, t=40, b=20), template='plotly_white')

    # Returner grafer OG traffiklys
    return fig_iaq, fig_eco2, fig_temp, fig_hum, fig_pressure, traffic_light_html, traffic_light_html

if __name__ == '__main__':
    print("Starter Dash server...")
    app.run(host='0.0.0.0', port=8080, debug=False)
