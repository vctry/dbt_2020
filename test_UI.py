import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import os
import glob

import pandas as pd
import plotly.graph_objs as go
from arima import *

INPUT_DIR = os.path.join(os.getcwd(), 'data')
file_name = 'result_data.csv'

load_data_dir = os.path.join(INPUT_DIR, file_name)
df = pd.read_csv(load_data_dir, engine='python', encoding='utf-8', index_col=None, header=0)
df = df[['created_at', 'created_year', 'created_month', 'area', 'vacancy']].dropna()

counter_vacancy = df.groupby(['area', 'created_year', 'created_month'], as_index=False)['vacancy'].count()
regions = list(df['area'].unique())
# regions.append('Все')

month = {'01': 'Январь', '02': 'Февраль', '03': 'Март', '04': 'Апрель', '05': 'Май', '06': 'Июнь',
         '07': 'Июль', '08': 'Август', '09': 'Сентябрь', '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'}

file_name = 'result_data_skills.csv'
load_data_dir = os.path.join(INPUT_DIR, file_name)
skills = pd.read_csv(load_data_dir, engine='python', encoding='utf-8', index_col=None, header=0)
skills = skills[['area', 'vacancy', 'created_month', 'created_year', 'key_skills']]
g_skills = skills.groupby(['key_skills', 'created_year', 'created_month'], as_index=False)['vacancy'].count()

skill_names = list(skills['key_skills'].unique())

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='region-column',
                    options=[{'label': i, 'value': i} for i in regions],
                    value='Москва'
                )
            ], style={'width': '69%', 'display': 'inline-block'}),
            html.Div([
                dcc.Dropdown(
                    id='year-slider',
                    options=[{'label': i, 'value': i} for i in ['2018', '2019', '2020']],
                    value='2020'
                )
            ], style={'width': '30%', 'display': 'inline-block'}),
        ], ),
        html.Div([
            dcc.Graph(id='graph-with-slider')], style={'display': 'inline-block'})
    ], style={'width': '40%', 'display': 'inline-block'}),
    html.Div([
        dcc.Graph(id='diagram')], style={'width': '40%', 'display': 'inline-block'})

])


@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('year-slider', 'value'),
     Input('region-column', 'value')])
def update_figure(year, region):
    traces = []
    y = counter_vacancy.loc[
        (counter_vacancy['created_year'] == int(year)) & (counter_vacancy['area'] == region), 'vacancy'].values
    x = list(month.values())
    traces.append(go.Scatter(
        x=x,
        y=y,
        text=f'Количество вакансий {region}',
        mode='markers+lines',
        opacity=0.7,
        marker={
            'size': 15,
            'line': {'width': 0.5, 'color': 'white'}
        },
        name='Счетчик вакансий в разные месяцы'
    ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'type': '-', 'title': 'Месяц'},
            yaxis={'title': 'Счетчик'},
            margin={'l': 80, 'b': 80, 't': 40, 'r': 40},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }


@app.callback(
    Output('diagram', 'figure'),
    [Input('region-column', 'value')])
def update_diagram(region):
    x = list(df.loc[(df['area'] == region), 'vacancy'].values)
    y_1 = list(counter_vacancy.loc[
                   (counter_vacancy['created_year'] == 2018) & (counter_vacancy['area'] == region), 'vacancy'])
    y_2 = list(counter_vacancy.loc[
                   (counter_vacancy['created_year'] == 2019) & (counter_vacancy['area'] == region), 'vacancy'])
    y_3 = list(counter_vacancy.loc[
                   (counter_vacancy['created_year'] == 2020) & (counter_vacancy['area'] == region), 'vacancy'])
    traces = []
    traces.append({
        'x': x,
        'y': y_1,
        'type': 'bar',
        'name': '2018'
    })
    traces.append({
        'x': x,
        'y': y_2,
        'type': 'bar',
        'name': '2019'
    })
    traces.append({
        'x': x,
        'y': y_3,
        'type': 'bar',
        'name': '2020'
    })

    return {
        'data': traces,
        'layout': {
            'title': 'Общая статистика',
            'color': '#7f7f7f',
            'xaxis': dict(color='#7f7f7f'),
            'barmode': 'stack',
            'colorway': ["#7a4c99", "#6f8bc7", "65c1ee"],
            'hovermode': "closest",
            'opacity': 0.7

        }
    }


@app.callback(
    Output('radar_chart', 'figure'),
    [Input('year-slider', 'value')])
def update_figure(year):
    traces = []
    data = g_skills.loc[(g_skills['created_year'] == int(year)), 'vacancy'].values
    labels = skill_names
    traces.append(go.Pie(
        labels=labels,
        values=data,
        textinfo='label+percent',
        insidetextorientation='radial',
        opacity=0.7,
        name='Распределение ключевых навыков по вакансиям'
    ))
    return {
        'data': traces,
        'layout': go.Layout(
            margin={'l': 80, 'b': 80, 't': 40, 'r': 40},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }


# @app.callback(
#     Output('graph-with-slider', 'figure'),
#     [Input('year-slider', 'value'),
#      Input('skills_down', 'value')])
# def update_figure(year, region):
#     traces = []
#     y = counter_vacancy.loc[
#         (counter_vacancy['created_year'] == int(year)) & (counter_vacancy['area'] == region), 'vacancy'].values
#     x = list(month.values())
#     traces.append(go.Scatter(
#         x=x,
#         y=y,
#         text=f'Количество вакансий {region}',
#         mode='markers+lines',
#         opacity=0.7,
#         marker={
#             'size': 15,
#             'line': {'width': 0.5, 'color': 'white'}
#         },
#         name='Счетчик вакансий в разные месяцы'
#     ))
#
#     return {
#         'data': traces,
#         'layout': go.Layout(
#             xaxis={'type': '-', 'title': 'Месяц'},
#             yaxis={'title': 'Счетчик'},
#             margin={'l': 80, 'b': 80, 't': 40, 'r': 40},
#             legend={'x': 0, 'y': 1},
#             hovermode='closest'
#         )
#     }


# @app.callback(
#     Output('indicator-graphic', 'figure'),
#     [Input('side_1', 'value'),
#      Input('side_2', 'value'),
#      Input('year-slider', 'value'),
#      Input('month--slider', 'value')])
# def update_graph(feat_1, feat_2, year, month):
#     dff = df.loc[(df['year'] == int(year)) & (df['month'] == month)]
#
#     return {
#         'data': [go.Scatter(
#             x=dff[feat_1],
#             y=dff[feat_2],
#             text=dff['region'],
#             mode='markers',
#             marker={
#                 'size': 15,
#                 'opacity': 0.5,
#                 'line': {'width': 0.5, 'color': 'white'}
#             }
#         )],
#         'layout': go.Layout(
#             xaxis={
#                 'title': feat_1
#             },
#             yaxis={
#                 'title': feat_2
#             },
#             margin={'l': 80, 'b': 0, 't': 40, 'r': 40},
#             hovermode='closest'
#         )
#     }


if __name__ == '__main__':
    app.run_server(debug=False)
