#!/usr/bin/env python
# -*- coding: utf-8 -*-


import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
import pycountry
import numpy as np
from dash.dependencies import Input, Output

# importing data from Kaggle data source as csv and change it to DataFrame
map_csv = pd.read_csv("who_suicide_statistics.csv")
df_map = pd.DataFrame(map_csv)

# Data refraction, some important countries(Iran and USA)
input_countries = df_map['country']

countries = {}
for country in pycountry.countries:
    countries[country.name] = country.alpha_3

country_codes = [countries.get(country, 'Unknown code') for country in input_countries]
df_map['iso_data'] = country_codes
df_map.loc[df_map.country == 'Iran (Islamic Rep of)', 'iso_data'] = 'IRN'
df_map.loc[df_map.country == 'United States of America', 'iso_data'] = 'USA'

# making df3 which will be used for some Diagarams
df3 = df_map.groupby(['country', 'iso_data', 'year'], as_index=False)['suicides_no', 'population'].sum()
df3['proportion'] = df3['suicides_no'] * 1000 / df3['population']

df3.replace([np.inf, -np.inf], np.nan, inplace=True)
df3.dropna()

# also df4 is important for another diagram
df4 = df3.loc[(df3 != 0).any(axis=1)].dropna().sort_values(by='proportion')

# list of options for the dropdown
options_list = [{'label': i, 'value': i} for i in df_map['country'].unique()]
options_list.insert(0, {'label': 'All', 'value': 'All'})

# beginning of the dash
app = dash.Dash(__name__)
server = app.server
# making the layout
app.title = 'LSMU Psychology'
app.layout = html.Div([dcc.Markdown(''' # General statistics of international suicide phenomenon'''),
                       dcc.Markdown('''## map of the world'''),
                       dcc.Markdown('''In the choropleth map below you can see absolute number of suicide deaths by each of the country in our data set.   
                                    please change the slider to see updated data for desired year.'''),

                       dcc.Graph(id="map_with_slider"),

                       dcc.Slider(
                           id='year_slider',
                           min=map_csv['year'].min(),
                           max=map_csv['year'].max(),
                           value=map_csv['year'].min(),
                           marks={str(year): str(year) for year in map_csv['year'].unique()},
                           tooltip={"placement": "bottom", "always_visible": True},
                           step=None
                       ),
                       dcc.Markdown('''## countries in comparison'''),
                       dcc.Markdown(
                           '''The left diagram shows the absolute count of suicide deaths in each country of the dataset and the right diagram shows relative number of suicide deaths in comparison to the population of the country.'''),

                       html.Div([
                           dcc.Graph(id="bar_chart")
                       ], style={'width': '49%', 'display': 'inline-block'}),

                       html.Div([
                           dcc.Graph(id="hbar_chart")
                       ], style={'width': '49%', 'display': 'inline-block'}),

                       dcc.Markdown('''## One country under the focus'''),
                       dcc.Markdown('''Here you can focus on one country and check the suicide trends which have been seperated by Gender and  Age group.  
                                    Here the suicide trends can be analyzed.'''),
                       html.Div([
                           dcc.Dropdown(id='country_picker', options=options_list, value='Lithuania')],
                           style={'width': '20%'}, title='please choose a country'),
                       dcc.Graph(id='one_country_chart'),
                       dcc.Markdown('''### Disclaimer: '''),
                       dcc.Markdown('''this project has been done by Ahmadreza Ramezanzadeh from group 49.  
 #### Reference: '''),
                       dcc.Markdown('''[united nations Developlemnt program](http://hdr.undp.org/en/indicators/137506) 2018 Human Development index  
                                    [kaggle] (https://www.kaggle.com/szamil/suicide-in-the-twenty-first-century/notebook) suicide in twenty first century  
                                    [world health organization](http://www.who.int/mental_health/suicide-prevention/en/) suicide prevention''')
                       ])


# the app contains two parts in ux first part give 3 results for the first part
@app.callback(Output('map_with_slider', 'figure'),
              Output('bar_chart', "figure"),
              Output('hbar_chart', 'figure'),
              Input('year_slider', 'value'))
def update_figure(selected_year):
    # 3 dataFrames for 3 diagrams
    filtered_df = df3[df3.year == selected_year]
    bar_df = df_map[df_map.year == selected_year]
    hbar_df = df4[df4.year == selected_year]

    # choroplethe map
    fig = px.choropleth(filtered_df, locations="iso_data",
                        color="suicides_no",
                        hover_name="country",
                        color_continuous_scale=px.colors.sequential.Plasma,
                        title='Number of suicide deaths in {}, world view'.format(selected_year))
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(transition_duration=100)

    # vertical bar chart

    bar_fig = px.bar(bar_df, x='country', y='suicides_no', color='sex',
                     title='Comparison of suicide deaths of each country in {}'.format(selected_year),
                     hover_data=['age'])
    # Horizental bar chart
    hbar_fig = px.bar(hbar_df, x=('proportion'), y=('country'), orientation='h',
                      title='Ranking of highest suicide mortality per capita in {}'.format(selected_year))
    return fig, bar_fig, hbar_fig


# second part of the app
@app.callback(Output('one_country_chart', 'figure'),
              Input('country_picker', 'value'))
def country_trend(selected_country):
    country_df = df_map[df_map.country == selected_country]

    country_fig = px.bar(country_df, x='year', y='suicides_no', color='sex',
                         title='follow up of the suicide deaths in {} through years'.format(selected_country),
                         hover_data=['age'])

    return country_fig


# server and render
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=False)
