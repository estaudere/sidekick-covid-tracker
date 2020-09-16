# Import required libraries
import os
import pickle
import copy
import datetime as dt
from datetime import date
import math

import requests
import pandas as pd
from flask import Flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

# Multi-dropdown options
from controls import BUILDINGS, BUILDING_COLORS

app = dash.Dash(__name__)
server = app.server

# Create controls
building_options = [{'label': str(BUILDINGS[building]), 'value': str(building)}
                  for building in BUILDINGS]

# well_status_options = [{'label': str(WELL_STATUSES[well_status]),
#                         'value': str(well_status)}
#                        for well_status in WELL_STATUSES]

# well_type_options = [{'label': str(WELL_TYPES[well_type]),
#                       'value': str(well_type)}
#                      for well_type in WELL_TYPES]


# Load data
today = date(2020, 9, 15).strftime('%d-%m-%Y') # date.today().strftime('%d-%m-%Y')
cases_today = pd.read_csv(f'./data/{today}.csv')
cases = pd.read_csv('./data/timeseries.csv')


# for mapbox??
# layout = dict(
#     autosize=True,
#     automargin=True,
#     margin=dict(
#         l=30,
#         r=30,
#         b=20,
#         t=40
#     ),
#     hovermode="closest",
#     plot_bgcolor="#F9F9F9",
#     paper_bgcolor="#F9F9F9",
#     legend=dict(font=dict(size=10), orientation='h'),
#     title='Satellite Overview',
#     mapbox=dict(
#         accesstoken=mapbox_access_token,
#         style="light",
#         center=dict(
#             lon=-78.05,
#             lat=42.54
#         ),
#         zoom=7,
#     )
# )


# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id='aggregate_data'),
        html.Div(
            [
                html.Div(
                    [
                        html.H2(
                            'Coppell High School COVID-19 Tracker',

                        ),
                        html.H4(
                            'The Sidekick. Last updated 9/15.',
                        )
                    ],

                    className='eight columns'
                ),
                # html.Img(
                #     src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe.png",
                #     className='two columns',
                # ),
                html.A(
                    html.Button(
                        "Visit Coppell Student Media",
                        id="learnMore"

                    ),
                    href="https://coppellstudentmedia.com/",
                    className="two columns"
                )
            ],
            id="header",
            className='row',
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            'Filter by building:',
                            className="control_label"
                        ),
                        dcc.RadioItems(
                            id='building_selector',
                            options=[
                                {'label': 'All ', 'value': 'all'},
                                {'label': 'Customize ', 'value': 'custom'}
                            ],
                            value='active',
                            labelStyle={'display': 'inline-block'},
                            className="dcc_control"
                        ),
                        dcc.Dropdown(
                            id='building',
                            options=building_options,
                            multi=True,
                            value=list(BUILDINGS.keys()),
                            className="dcc_control"
                        ),
                    ],
                    className="pretty_container four columns"
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P("Staff"),
                                        html.H6(
                                            id="staff_text",
                                            className="info_text"
                                        )
                                    ],
                                    id="staff",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.P("In person"),
                                                html.H6(
                                                    id="inpersonText",
                                                    className="info_text"
                                                )
                                            ],
                                            id="inperson",
                                            className="pretty_container"
                                        ),
                                        html.Div(
                                            [
                                                html.P("Remote"),
                                                html.H6(
                                                    id="remoteText",
                                                    className="info_text"
                                                )
                                            ],
                                            id="remote",
                                            className="pretty_container"
                                        ),
                                        html.Div(
                                            [
                                                html.P("Other"),
                                                html.H6(
                                                    id="otherText",
                                                    className="info_text"
                                                )
                                            ],
                                            id="other",
                                            className="pretty_container"
                                        ),
                                        html.Div(
                                            [
                                                dcc.DatePickerSingle(
                                                    id='my-date-picker-single',
                                                    # date=get_date() # for testing purpose
                                                    date=today # Actual code
                                                )
                                            ], style= {'display': 'none'}
                                        )
                                    ],
                                    id="tripleContainer",
                                )

                            ],
                            id="infoContainer",
                            className="row"
                        ),
                        html.Div(
                            [
                                dcc.Graph(
                                    id='count_graph',
                                )
                            ],
                            id="countGraphContainer",
                            className="pretty_container"
                        )
                    ],
                    id="rightCol",
                    className="eight columns"
                )
            ],
            className="row"
        ),
    ],
    id="mainContainer",
    style={
        "display": "flex",
        "flex-direction": "column"
    }
)


# Helper functions
def human_format(num):

    # magnitude = int(math.log(num, 1000))
    # mantissa = str(int(num / (1000**magnitude)))
    return num


def filter_dataframe(df, building, date):
    if date:
        dff = df[(df.building == building) & (df.timestamp == date)]
    else:
        dff = df[(df.building == building)]
    return dff


# def fetch_individual(api):
#     try:
#         points[api]
#     except:
#         return None, None, None, None

#     index = list(range(min(points[api].keys()), max(points[api].keys()) + 1))
#     gas = []
#     oil = []
#     water = []

#     for year in index:
#         try:
#             gas.append(points[api][year]['Gas Produced, MCF'])
#         except:
#             gas.append(0)
#         try:
#             oil.append(points[api][year]['Oil Produced, bbl'])
#         except:
#             oil.append(0)
#         try:
#             water.append(points[api][year]['Water Produced, bbl'])
#         except:
#             water.append(0)

#     return index, gas, oil, water

# indicator boxes
def fetch_chs(df, today):

    dff = filter_dataframe(df, 'Coppell High School', today)
    staff = [dff["staff"]]
    inperson = [dff["inperson"]]
    remote = [dff["remote"]]
    other = [dff["other"]]

    return staff, inperson, remote, other


# Create callbacks
@app.callback(Output('aggregate_data', 'data'),
            [Input('my-date-picker-single', 'date')])

def update_production_text(today):
    staff, inperson, remote, other, total = fetch_chs(cases, today)
    return [human_format(sum(staff)), human_format(sum(inperson)), human_format(sum(remote))]


# Radio -> multi
@app.callback(Output('building', 'value'),
              [Input('building_selector', 'value')])
def display_status(selector):
    if selector == 'all':
        return list(BUILDINGS.keys())
    else:
        return []


# Radio -> multi
# @app.callback(Output('well_types', 'value'),
#               [Input('well_type_selector', 'value')])
# def display_type(selector):
#     if selector == 'all':
#         return list(WELL_TYPES.keys())
#     elif selector == 'productive':
#         return ['GD', 'GE', 'GW', 'IG', 'IW', 'OD', 'OE', 'OW']
#     else:
#         return []


# # Slider -> count graph
# @app.callback(Output('year_slider', 'value'),
#               [Input('count_graph', 'selectedData')])
# def update_year_slider(count_graph_selected):

#     if count_graph_selected is None:
#         return [1990, 2010]
#     else:
#         nums = []
#         for point in count_graph_selected['points']:
#             nums.append(int(point['pointNumber']))

#         return [min(nums) + 1960, max(nums) + 1961]


# # Selectors -> well text
# @app.callback(Output('well_text', 'children'),
#               [Input('well_statuses', 'value'),
#                Input('well_types', 'value'),
#                Input('year_slider', 'value')])
# def update_well_text(well_statuses, well_types, year_slider):

#     dff = filter_dataframe(df, well_statuses, well_types, year_slider)
#     return dff.shape[0]


# indicator text boxes

@app.callback(Output('gasText', 'children'),
              [Input('aggregate_data', 'data')])
def update_gas_text(data):
    return data[0] + " cases"


@app.callback(Output('oilText', 'children'),
              [Input('aggregate_data', 'data')])
def update_oil_text(data):
    return data[1] + " cases"


@app.callback(Output('waterText', 'children'),
              [Input('aggregate_data', 'data')])
def update_water_text(data):
    return data[2] + " cases"


# Selectors -> main graph SCATTER

@app.callback(Output('main_graph', 'figure'),
              [Input('building', 'value')])
def make_main_figure(building, selector, main_graph_layout):

    traces = []
    for building, date in cases.groupby('building'):
        dff = filter_dataframe(cases, building)
        trace = dict(
            ttype='scatter',
            mode='lines',
            name='Cases',
            x=dff['timestamp'],
            y=dff['total'],
            line=dict(
                shape="spline",
                smoothing="2",
                color=BUILDING_COLORS[building]
            )
        )
        traces.append(trace)

    # if (main_graph_layout is not None and 'locked' in selector):

    #     lon = float(main_graph_layout['mapbox']['center']['lon'])
    #     lat = float(main_graph_layout['mapbox']['center']['lat'])
    #     zoom = float(main_graph_layout['mapbox']['zoom'])
    #     layout['mapbox']['center']['lon'] = lon
    #     layout['mapbox']['center']['lat'] = lat
    #     layout['mapbox']['zoom'] = zoom
    # else:
    #     lon = -78.05
    #     lat = 42.54
    #     zoom = 7

    figure = dict(data=traces)
    return figure


# Main graph -> individual graph
# @app.callback(Output('individual_graph', 'figure'),
#               [Input('main_graph', 'hoverData')])
# def make_individual_figure(main_graph_hover):

#     layout_individual = copy.deepcopy(layout)

#     if main_graph_hover is None:
#         main_graph_hover = {'points': [{'curveNumber': 4,
#                                         'pointNumber': 569,
#                                         'customdata': 31101173130000}]}

#     chosen = [point['customdata'] for point in main_graph_hover['points']]
#     index, gas, oil, water = fetch_individual(chosen[0])

#     if index is None:
#         annotation = dict(
#             text='No data available',
#             x=0.5,
#             y=0.5,
#             align="center",
#             showarrow=False,
#             xref="paper",
#             yref="paper"
#         )
#         layout_individual['annotations'] = [annotation]
#         data = []
#     else:
#         data = [
#             dict(
#                 type='scatter',
#                 mode='lines+markers',
#                 name='Gas Produced (mcf)',
#                 x=index,
#                 y=gas,
#                 line=dict(
#                     shape="spline",
#                     smoothing=2,
#                     width=1,
#                     color='#fac1b7'
#                 ),
#                 marker=dict(symbol='diamond-open')
#             ),
#             dict(
#                 type='scatter',
#                 mode='lines+markers',
#                 name='Oil Produced (bbl)',
#                 x=index,
#                 y=oil,
#                 line=dict(
#                     shape="spline",
#                     smoothing=2,
#                     width=1,
#                     color='#a9bb95'
#                 ),
#                 marker=dict(symbol='diamond-open')
#             ),
#             dict(
#                 type='scatter',
#                 mode='lines+markers',
#                 name='Water Produced (bbl)',
#                 x=index,
#                 y=water,
#                 line=dict(
#                     shape="spline",
#                     smoothing=2,
#                     width=1,
#                     color='#92d8d8'
#                 ),
#                 marker=dict(symbol='diamond-open')
#             )
#         ]
#         layout_individual['title'] = dataset[chosen[0]]['Well_Name']

#     figure = dict(data=data, layout=layout_individual)
#     return figure


# Selectors, main graph -> aggregate graph THIS IS THE ONE WE WANT
# @app.callback(Output('aggregate_graph', 'figure'),
#               [Input('building', 'value'),
#                Input('well_types', 'value'),
#                Input('year_slider', 'value'),
#                Input('main_graph', 'hoverData')])
# def make_aggregate_figure(well_statuses, well_types, year_slider,
#                           main_graph_hover):

#     layout_aggregate = copy.deepcopy(layout)

#     if main_graph_hover is None:
#         main_graph_hover = {'points': [{'curveNumber': 4, 'pointNumber': 569,
#                                         'customdata': 31101173130000}]}

#     chosen = [point['customdata'] for point in main_graph_hover['points']]
#     well_type = dataset[chosen[0]]['Well_Type']
#     dff = filter_dataframe(df, well_statuses, well_types, year_slider)

#     selected = dff[dff['Well_Type'] == well_type]['API_WellNo'].values
#     index, gas, oil, water = fetch_aggregate(selected, year_slider)

#     data = [
#         dict(
#             type='scatter',
#             mode='lines',
#             name='Gas Produced (mcf)',
#             x=index,
#             y=gas,
#             line=dict(
#                 shape="spline",
#                 smoothing="2",
#                 color='#F9ADA0'
#             )
#         ),
#         dict(
#             type='scatter',
#             mode='lines',
#             name='Oil Produced (bbl)',
#             x=index,
#             y=oil,
#             line=dict(
#                 shape="spline",
#                 smoothing="2",
#                 color='#849E68'
#             )
#         ),
#         dict(
#             type='scatter',
#             mode='lines',
#             name='Water Produced (bbl)',
#             x=index,
#             y=water,
#             line=dict(
#                 shape="spline",
#                 smoothing="2",
#                 color='#59C3C3'
#             )
#         )
#     ]
#     layout_aggregate['title'] = 'Aggregate: ' + WELL_TYPES[well_type]

#     figure = dict(data=data, layout=layout_aggregate)
#     return figure


# Selectors, main graph -> pie graph
# @app.callback(Output('pie_graph', 'figure'),
#               [Input('well_statuses', 'value'),
#                Input('well_types', 'value'),
#                Input('year_slider', 'value')])
# def make_pie_figure(well_statuses, well_types, year_slider):

#     layout_pie = copy.deepcopy(layout)

#     dff = filter_dataframe(df, well_statuses, well_types, year_slider)

#     selected = dff['API_WellNo'].values
#     index, gas, oil, water = fetch_aggregate(selected, year_slider)

#     aggregate = dff.groupby(['Well_Type']).count()

#     data = [
#         dict(
#             type='pie',
#             labels=['Gas', 'Oil', 'Water'],
#             values=[sum(gas), sum(oil), sum(water)],
#             name='Production Breakdown',
#             text=['Total Gas Produced (mcf)', 'Total Oil Produced (bbl)',
#                   'Total Water Produced (bbl)'],
#             hoverinfo="text+value+percent",
#             textinfo="label+percent+name",
#             hole=0.5,
#             marker=dict(
#                 colors=['#fac1b7', '#a9bb95', '#92d8d8']
#             ),
#             domain={"x": [0, .45], 'y':[0.2, 0.8]},
#         ),
#         dict(
#             type='pie',
#             labels=[WELL_TYPES[i] for i in aggregate.index],
#             values=aggregate['API_WellNo'],
#             name='Well Type Breakdown',
#             hoverinfo="label+text+value+percent",
#             textinfo="label+percent+name",
#             hole=0.5,
#             marker=dict(
#                 colors=[WELL_COLORS[i] for i in aggregate.index]
#             ),
#             domain={"x": [0.55, 1], 'y':[0.2, 0.8]},
#         )
#     ]
#     layout_pie['title'] = 'Production Summary: {} to {}'.format(
#         year_slider[0], year_slider[1])
#     layout_pie['font'] = dict(color='#777777')
#     layout_pie['legend'] = dict(
#         font=dict(color='#CCCCCC', size='10'),
#         orientation='h',
#         bgcolor='rgba(0,0,0,0)'
#     )

#     figure = dict(data=data, layout=layout_pie)
#     return figure


# Selectors -> count graph
# @app.callback(Output('count_graph', 'figure'),
#               [Input('well_statuses', 'value'),
#                Input('well_types', 'value'),
#                Input('year_slider', 'value')])
# def make_count_figure(well_statuses, well_types, year_slider):

#     layout_count = copy.deepcopy(layout)

#     dff = filter_dataframe(df, well_statuses, well_types, [1960, 2017])
#     g = dff[['API_WellNo', 'Date_Well_Completed']]
#     g.index = g['Date_Well_Completed']
#     g = g.resample('A').count()

#     colors = []
#     for i in range(1960, 2018):
#         if i >= int(year_slider[0]) and i < int(year_slider[1]):
#             colors.append('rgb(123, 199, 255)')
#         else:
#             colors.append('rgba(123, 199, 255, 0.2)')

#     data = [
#         dict(
#             type='scatter',
#             mode='markers',
#             x=g.index,
#             y=g['API_WellNo'] / 2,
#             name='All Wells',
#             opacity=0,
#             hoverinfo='skip'
#         ),
#         dict(
#             type='bar',
#             x=g.index,
#             y=g['API_WellNo'],
#             name='All Wells',
#             marker=dict(
#                 color=colors
#             ),
#         ),
#     ]

#     layout_count['title'] = 'Completed Wells/Year'
#     layout_count['dragmode'] = 'select'
#     layout_count['showlegend'] = False
#     layout_count['autosize'] = True

#     figure = dict(data=data, layout=layout_count)
#     return figure


# Main
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)