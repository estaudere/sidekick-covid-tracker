import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
from datetime import date
import os

# os.chdir('./data')
today = date.today().strftime('%d-%m-%Y')
cases_today = pd.read_csv(f'./data/{today}.csv')

app = dash.Dash()

markdown_text = '''
# Coppell High School COVID-19 Tracker
This webapp was created by Neha Desaraju, entertainment editor. Last updated 9/15/20.

For more information, visit [Coppell ISD's COVID-19 Dashboard](https://www.coppellisd.com/COVID-19Dashboard).
'''

fig = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cases_today.at[14, "inperson"],
    title = {"text": "In-person cases<br>"},
    delta = {'reference': 0, 'increasing': {'color': '#FF4136'}, 'decreasing': {'color': '#3D9970'}},
    domain = {'x': [0.5, 1], 'y': [0, 1]}))

fig.add_trace(go.Indicator(
    mode = "number+delta",
    value = cases_today.at[14, "staff"],
    delta = {'reference': 0, 'increasing': {'color': '#FF4136'}, 'decreasing': {'color': '#3D9970'}},
    title = {"text": "Staff cases<br>"},
    domain = {'x': [0, 0.5], 'y': [0, 1]}))

fig.update_layout(paper_bgcolor = "lightgray")



colors = {
    'background': '#FFFFFF',
    'text': '#000000'
}

app.layout = html.Div(className="app-header", children=[
    html.Div([
    dcc.Markdown(children=markdown_text, style={
            'textAlign': 'center',
            'color': colors['text']
    })
    ]),

    dcc.Graph(
        id='Graph1',
        figure=fig
    )
])


if __name__ == '__main__':
  app.run_server(port=8080, debug=True)