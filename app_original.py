# -*- coding: utf-8 -*-
"""
Created on Feb 17 2023

@author: Mikkel

"""

import os 
import pandas as pd
import json
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
import dash_bootstrap_components as dbc

os.chdir('C:/Users/mikke/OneDrive - Syddansk Universitet/Projects/vildtudbytte') #set path



'''
Load data, color palette & variables for callback
'''



with open('dansk_kommuner_geojson.json', encoding='utf-8') as response:
    kommuner = json.load(response)

df = pd.read_csv("taken_game.csv")

df_detailed = pd.read_csv("data_detailed.csv")

color_palette_detailed = ['#66c2a5', '#fc8d62', '#8da0cb']

max_year = df['Year'].max()
min_year = df['Year'].min()

species_options = [{'label': str(species_), 'value': species_} for species_ in df['Species'].unique()]



'''
LAYOUT
'''



app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dcc.Location(id='url', refresh=True),
    dbc.Row([       
        dbc.Col([
            dbc.Button("Reset", outline=True, size="lg", color="danger", className="me-1", style={'margin-top': '20px'}, id='refresh-button'),
        ], width=1),
        dbc.Col([
            dcc.Graph(id="species_sunburst", style={'margin-top': '20px', 'margin-bottom': '40px'}), 
        ], width=5),

        dbc.Col([
            dcc.Graph(id="map", style={'margin-top': '40px', 'margin-bottom': '40px', "height": "70vh"}),
        ], width=6)
        
    ]),

    dbc.Row([
        dbc.Col([
            dcc.RangeSlider(
                id='range_slider',
                min=min_year,
                max=max_year,
                step=10,
                value=[min_year, max_year],
                allowCross=True,
                pushable=1,
                marks={i: {'label': str(i), 'style': {'font-size': '14px'}} for i in range(min_year, max_year + 1)}
            ),
        ], width=12)
    ]),


    dbc.Row([
        dbc.Col([
            html.Div([
            html.Div(dcc.Graph(id="kommune_graph"), id="div_kommune_graph", style={'display': 'inline-block', 'width': '100%'}),
            html.Div(dcc.Graph(id="kommune_graph_2"), id="div_kommune_graph_2", style={'display': 'inline-block', 'width': '0%'})
            ], style={'display': 'flex', 'flex-direction': 'row'})
        ]),
    ]),

    dbc.Row([
        dbc.Col([
            html.Div(id="detailed_graph_container", children=[
                dcc.Graph(id="detailed_graph")
            ], style={'display': 'none'})
        ])
    ])

], fluid=True)

app.layout.children.append(dcc.Store(id='selected_kommunes', data=[]))



'''
SUNBURST
'''



@app.callback(
    Output('species_sunburst', 'figure'), 
    [Input("range_slider", "value"),
     Input("selected_kommunes", "data")]
)

def update_sunburst(selected_years, selected_kommunes):
    
    if not selected_kommunes:
        filtered_df = df[
        (df['Year'] >= selected_years[0]) &
        (df['Year'] <= selected_years[1])]
        
    else:
        filtered_df = df[(df['Kommune'].isin(selected_kommunes)) &
        (df['Year'] >= selected_years[0]) &
        (df['Year'] <= selected_years[1])]

    filtered_df['Taken game log'] = np.log(filtered_df['Taken game'] + 1)

    fig = px.sunburst(
        data_frame=filtered_df,  
        width=475,
        height=475,
        path=["Group", "Species"],
        color="Group",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        values='Taken game log',
    )

    fig.update_traces(
        maxdepth=2,
        insidetextorientation='radial'
    )

    fig.update_layout(
        margin=dict(t=10, l=10, r=10, b=10)
    )

    fig.update_traces(hovertemplate='%{label}')

    return fig



'''
MAP
'''



@app.callback(
    Output("map", "figure"), 
    [Input("range_slider", "value"),
     Input("species_sunburst", "clickData"), 
     Input("selected_kommunes", "data")]
)
def display_map(selected_years, sunburst_click_data, selected_kommunes):

    selected_label = None
    if sunburst_click_data:
        selected_label = sunburst_click_data['points'][0]['label']
    hover_label = selected_label if selected_label else "Alle arter/grupper"

    if sunburst_click_data:
        selected_species = sunburst_click_data['points'][0]['label']
    else:
        selected_species = None

    filtered_df = df[(df['Year'] >= selected_years[0]) &
                     (df['Year'] <= selected_years[1])]
    
    var = 'Taken game'                 
    if selected_species in set(filtered_df['Species']):
        filtered_df = filtered_df[filtered_df['Species'] == selected_species]
    elif selected_species in set(filtered_df['Group']):
        filtered_df = filtered_df[filtered_df['Group'] == selected_species]
        var = 'Taken game group'

    df_grouped = filtered_df.groupby(['Kommune', 'Year'])[var].sum().reset_index()
    
    def calculate_change(group):
        if selected_species == None:
            baseline_value = np.sum(group[group['Year'] == selected_years[0]]['Taken game'])
            group['Procentvis ændring'] = (group['Taken game'] - baseline_value) / baseline_value * 100
            group['TakenGameYearStart'] = np.sum(group[group['Year'] == selected_years[0]]['Taken game'])
            group['TakenGameYearEnd'] = np.sum(group[group['Year'] == selected_years[1]]['Taken game'])
        else:
            baseline_value = group[group['Year'] == selected_years[0]][var].iloc[0]
            group['Procentvis ændring'] = (group[var] - baseline_value) / baseline_value * 100
            group['TakenGameYearStart'] = group[group['Year'] == selected_years[0]][var].values[0]
            group['TakenGameYearEnd'] = group[group['Year'] == selected_years[1]][var].values[0]
        return group
    
    
    df_grouped = df_grouped.groupby('Kommune').apply(calculate_change)

    df_grouped['CustomHoverText'] = df_grouped['Kommune'] + '<br>' + \
                                      'Procentvis ændring: ' + df_grouped['Procentvis ændring'].round(2).astype(str) + ' %' + '<br>' + \
                                      'Nedlagt vildt i ' + str(selected_years[0]) + ': ' + df_grouped['TakenGameYearStart'].astype(str) + '<br>' + \
                                      'Nedlagt vildt i ' + str(selected_years[1]) + ': ' + df_grouped['TakenGameYearEnd'].astype(str) + '<br>' + \
                                      'Viser: ' + str(hover_label)

    fig = px.choropleth_mapbox(
        df_grouped, 
        geojson=kommuner, 
        locations='Kommune',  
        featureidkey="properties.navn",  
        color='Procentvis ændring',
        color_continuous_scale="RdBu",
        range_color=[-150, 150],
        color_continuous_midpoint=0,
        center={"lat": 55.9581, "lon": 9.8476},  
        zoom=5.5, 
        mapbox_style="open-street-map"
    )

    fig.update_mapboxes(
    bounds_east=16.7,
    bounds_west=7.5,    
    bounds_south=54.5,  
    bounds_north=57.9   
)

    

    fig.update_traces(hovertemplate=df_grouped["CustomHoverText"])

    for kommune in selected_kommunes:
        df_kommune = df_grouped[df_grouped['Kommune'] == kommune]
        fig.add_trace(
            go.Choroplethmapbox(
                geojson=kommuner, 
                locations=df_kommune['Kommune'], 
                featureidkey="properties.navn",
                z=df_kommune['Percentage Change'],  
                colorscale=[[0, 'rgba(80, 80, 80, 1.0)'], [1, 'rgba(80, 80, 80, 1.0)']], 
                showscale=False, 
                text=df_kommune['CustomHoverText'],
                hoverinfo='text',
                name=''
            )
        )

    
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig



'''
SELECTIONS ON MAP STORED
'''



@app.callback(
    Output('selected_kommunes', 'data'),
    Input('map', 'clickData'),
    State('selected_kommunes', 'data')
)
def store_clicked_kommunes(clickData, selected_kommunes):
    if clickData is None:
        raise dash.exceptions.PreventUpdate

    clicked_kommune = clickData['points'][0]['location']

    if clicked_kommune in selected_kommunes:
        selected_kommunes.remove(clicked_kommune)

    else:
        selected_kommunes.append(clicked_kommune)

    return selected_kommunes



'''
GRAPH SPECIES
'''



@app.callback(
    Output("kommune_graph", "figure"),
    [Input("selected_kommunes", "data"),
     Input("range_slider", "value"),
     Input("species_sunburst", "clickData")] 
)
def update_kommune_graph(selected_kommunes, selected_years, sunburst_click_data):   
    
    selected_species = sunburst_click_data['points'][0]['label'] if sunburst_click_data else None


    selected_item = sunburst_click_data['points'][0]['label'] if sunburst_click_data else None
    is_species = selected_item in set(df['Species'])
    is_group = selected_item in set(df['Group']) and not is_species
    
    if selected_species not in set(df['Species']):
        selected_species = None
    
    fig = go.Figure()

    title = "Nedlagt vildt"

    if is_species:
        title += " af art: " + selected_item  
    elif is_group:
     title += " af gruppe: " + selected_item    

    if selected_kommunes:
        kommune_list = ", ".join(selected_kommunes)
        title += "<br>I kommuner: " + kommune_list 
    else:
        title += "<br>I Kommuner: Alle kommuner"           

    if not selected_kommunes:
        filtered_df = df[(df['Year'] >= selected_years[0]) & (df['Year'] <= selected_years[1])]
        
        if selected_species:
            filtered_df = filtered_df[filtered_df['Species'] == selected_species]

        aggregated_df = filtered_df.groupby('Year')['Taken game'].sum().reset_index()
        

        all_kommunes_hovertemplate = "<b>Alle Kommuner</b><br>" + \
                                    "<b>%{x}</b><br>" + \
                                    "Nedlagt: <b>%{y:,.0f}</b><br><extra></extra>"
        
        fig.add_trace(go.Scatter(x=aggregated_df["Year"], y=aggregated_df["Taken game"],
                                 mode='lines+markers',
                                 hovertemplate=all_kommunes_hovertemplate,
                                 name='All Kommunes'))
        
        x = aggregated_df['Year']
        y = aggregated_df['Taken game']
        m, b = np.polyfit(x, y, 1)

        fig.add_trace(go.Scatter(x=x, y=m * x + b,
                             mode='lines',
                             name='Tendenslinje',
                             line=dict(color='black', dash='dash'),
                             hoverinfo='none'))  

    else:
        all_kommunes_df = pd.DataFrame()
        for kommune in selected_kommunes:
            filtered_df = df[(df['Kommune'] == kommune) &
                             (df['Year'] >= selected_years[0]) &
                             (df['Year'] <= selected_years[1])]
            if selected_species:
                filtered_df = filtered_df[filtered_df['Species'] == selected_species]
            elif selected_species == None:
                filtered_df = filtered_df.groupby(['Year'])['Taken game'].sum().reset_index()
            
            all_kommunes_df = pd.concat([all_kommunes_df, filtered_df], ignore_index=True)

            kommune_hovertemplate = f"<b>{kommune}</b><br>" + \
                                    "<b>%{x}</b><br>" + \
                                    "Nedlagt: <b>%{y:,.0f}</b><br><extra></extra>"
            
            fig.add_trace(go.Scatter(x=filtered_df["Year"], y=filtered_df["Taken game"],
                                     mode='lines+markers',
                                     hovertemplate=kommune_hovertemplate,
                                     name=kommune))
        x = all_kommunes_df['Year']
        y = all_kommunes_df['Taken game']
        m, b = np.polyfit(x, y, 1)
        
        fig.add_trace(go.Scatter(x=x, y=m * x + b,
                             mode='lines',
                             name='Tendenslinje',
                             line=dict(color='black', dash='dash'),
                             hoverinfo='none'))  

    fig.update_layout(
    title={
        'text': title,
        'y': 0.9,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': dict(size=16) 
    },
    legend=dict(itemclick=False, itemdoubleclick=False),
    showlegend=True if selected_species is None else False,
    plot_bgcolor="#FFFFFF",
    title_pad=dict(t=20),
    font=dict(size=14),  
    height=450,
    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey'),
    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey'),
)

    
    pastel_colors = px.colors.qualitative.Pastel
    for i, trace in enumerate(fig.data):
        if trace.name != 'Tendenslinje': 
            fig.data[i].line.color = pastel_colors[i % len(pastel_colors)]
            fig.update_xaxes(dtick=1)
    
    fig.update_xaxes(dtick=1)

    return fig



'''
GRAPH GROUPS
'''



@app.callback(
    [Output("kommune_graph_2", "figure"),
     Output("div_kommune_graph", "style"),
     Output("div_kommune_graph_2", "style")],
    [Input("selected_kommunes", "data"),
     Input("range_slider", "value"),
     Input("species_sunburst", "clickData")]
)
def update_kommune_graph(selected_kommunes, selected_years, sunburst_click_data):
    if not sunburst_click_data:
        raise dash.exceptions.PreventUpdate

    selected_species = sunburst_click_data['points'][0]['label'] if sunburst_click_data else None

    title_group = None

    if sunburst_click_data:
        selected_label = sunburst_click_data['points'][0]['label']
        
        if selected_label in df['Species'].unique():
            
            title_group = df[df['Species'] == selected_label]['Group'].iloc[0]
        elif selected_label in df['Group'].unique():
            
            title_group = selected_label

    
    if selected_kommunes:
        kommunes_str = ', '.join(selected_kommunes)
        dynamic_title = f"Nedlagt vildt i gruppe: {title_group} <br>I Kommuner: {kommunes_str}"
    else:
        dynamic_title = f"Nedlagt vildt i gruppe: {title_group} <br> I kommuner: Alle kommuner"
    
    fig = go.Figure()
    is_true = False
    
    if not selected_kommunes:
        filtered_df = df[(df['Year'] >= selected_years[0]) & (df['Year'] <= selected_years[1])]
        
        if selected_species in set(df['Species']):
            filtered_df = filtered_df[filtered_df['Species'] == selected_species]
            aggregated_df = filtered_df.groupby('Year')['Taken game group'].sum().reset_index()
            
        elif selected_species in set(filtered_df['Group']):
            filtered_df = filtered_df[filtered_df['Group'] == selected_species]
            aggregated_df = filtered_df.groupby(['Year'])['Taken game'].sum().reset_index()
            aggregated_df = aggregated_df.rename(columns = {'Taken game':'Taken game group'})
            is_true = True
            
        all_kommunes_hovertemplate = "<b>Alle kommuner</b><br>" + \
                                 "<b>%{x}</b><br>" + \
                                 "Nedlagt: <b>%{y:,.0f}</b><br><extra></extra>"
        
        fig.add_trace(go.Scatter(x=aggregated_df["Year"], y=aggregated_df["Taken game group"],
                                mode='lines+markers',
                                name='All Kommunes',
                                hovertemplate=all_kommunes_hovertemplate))
    
        x = aggregated_df['Year']
        y = aggregated_df['Taken game group']
        m, b = np.polyfit(x, y, 1)
        
        fig.add_trace(go.Scatter(x=x, y=m * x + b,
                             mode='lines',
                             name='Tendenslinje',
                             line=dict(color='black', dash='dash'),
                             hoverinfo='none'))  
    
    all_kommunes_df = pd.DataFrame()
    for kommune in selected_kommunes:
        filtered_df = df[(df['Kommune'] == kommune) &
                         (df['Year'] >= selected_years[0]) &
                         (df['Year'] <= selected_years[1])]
        if selected_species in set(filtered_df['Species']): 
            filtered_df = filtered_df[filtered_df['Species'] == selected_species]
        elif selected_species in set(filtered_df['Group']):
            filtered_df = filtered_df[filtered_df['Group'] == selected_species]
            is_true = True
        else:
            filtered_df = filtered_df.groupby(['Year'])['Taken game group'].sum().reset_index()
        
        all_kommunes_df = pd.concat([all_kommunes_df, filtered_df], ignore_index=True)

        kommune_hovertemplate = f"<b>{kommune}</b><br>" + \
                            "<b>%{x}</b><br>" + \
                            "Nedlagt: <b>%{y:,.0f}</b><br><extra></extra>"
        
        fig.add_trace(go.Scatter(x=filtered_df["Year"], 
                                 y=filtered_df["Taken game group"],
                                 mode='lines+markers',
                                 name=kommune,
                                 hovertemplate=kommune_hovertemplate
                                 ))
    
    if not all_kommunes_df.empty:
        
        x = all_kommunes_df['Year']
        y = all_kommunes_df['Taken game group']
        m, b = np.polyfit(x, y, 1)
        
        fig.add_trace(go.Scatter(x=x, y=m * x + b,
                                 mode='lines',
                                 name='Tendenslinje',  
                                 line=dict(color='black', dash='dash'),
                                 hoverinfo='none'))
        
    fig.update_layout(
    title={
        'text': dynamic_title,  
        'y': 0.9,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': dict(size=16)  
    },
    legend=dict(itemclick=False, itemdoubleclick=False),
    plot_bgcolor="#FFFFFF",
    title_pad=dict(t=20),
    font=dict(size=14),  
    height=450,
    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey'),
    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey'),
)


    pastel_colors = px.colors.qualitative.Pastel
    for i, trace in enumerate(fig.data):
        if trace.name != 'Tendenslinje': 
            fig.data[i].line.color = pastel_colors[i % len(pastel_colors)]
            fig.update_xaxes(dtick=1)

    if is_true:
        return fig, {'display': 'inline-block', 'width': '0%'}, {'display': 'inline-block', 'width': '100%'}
    else:
        return fig, {'display': 'inline-block', 'width': '50%'}, {'display': 'inline-block', 'width': '50%'}



'''
GRAPH DETAILED
'''



@app.callback(
    [Output("detailed_graph", "figure"), 
     Output("detailed_graph_container", "style")],
    [Input("selected_kommunes", "data"),
     Input("range_slider", "value"),
     Input("species_sunburst", "clickData")] 
)

def update_type_proportion_graph(selected_kommunes, selected_years, sunburst_click_data):
        
    selected_species = sunburst_click_data['points'][0]['label'] if sunburst_click_data else None

    if not selected_species:
        raise dash.exceptions.PreventUpdate

    if not selected_kommunes:
        filtered_df = df_detailed[
        (df_detailed['Year'] >= selected_years[0]) &
        (df_detailed['Year'] <= selected_years[1]) &
        (df_detailed['Species'] == selected_species)
    ]

    else:
        filtered_df = df_detailed[
        (df_detailed['Kommune'].isin(selected_kommunes)) &
        (df_detailed['Year'] >= selected_years[0]) &
        (df_detailed['Year'] <= selected_years[1]) &
        (df_detailed['Species'] == selected_species)
    ]

    if filtered_df.empty:
        return {}, {'display': 'none'}

    df_grouped = filtered_df.groupby(['Year', 'Type'])['Total'].sum().reset_index()
    year_total = df_grouped.groupby('Year')['Total'].sum().reset_index()
    year_total = year_total.rename(columns={'Total': 'Year_Total'})
    df_grouped = df_grouped.merge(year_total, on='Year')
    df_grouped['Percentage'] = ((df_grouped['Total'] / df_grouped['Year_Total']) * 100).round(2)

    kommunes_str = ", ".join(selected_kommunes) if selected_kommunes else "Alle kommuner"
    title = f"Andel fordelt på type: {selected_species}<br>I kommuner: {kommunes_str}"

    fig = px.bar(
    df_grouped,
    barmode="group",
    x='Year', 
    y='Percentage',
    color='Type',
    hover_data={
        'Type': True, 
        'Total': ':.0f', 
        'Percentage': ':.2f%'  
    },
    custom_data=['Type', 'Percentage'],  
    title=title,
    color_discrete_sequence=color_palette_detailed
)

    hovertemplate = "<b>%{customdata[0]}</b><br>" + \
                "<b>%{x}</b><br>" + \
                "Andel: <b>%{customdata[1]} %</b><extra></extra>"

    for trace in fig.data:
        trace.hovertemplate = hovertemplate

    fig.update_xaxes(dtick=1, title='')  
    fig.update_yaxes(title='')  
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(title='Procent')

    fig.update_layout(
    title={
        'text': title,  
        'y': 0.9,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': dict(size=18)  
    },
    
        hovermode='closest',
        plot_bgcolor="#FFFFFF",
        title_pad=dict(t=20),
        font=dict(size=14),
        height=425,
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey'),
        legend_title_text=''
    )

    return fig, {'display': 'block'}



'''
RESET BUTTON
'''



@app.callback(
    Output('url', 'href'),
    [Input('refresh-button', 'n_clicks')],
    prevent_initial_call=True 
)
def refresh_page(n_clicks):
    if n_clicks:
        return '/'  

    raise dash.exceptions.PreventUpdate



'''
RUN SERVER
'''



if __name__ == '__main__':
    app.run_server()
    