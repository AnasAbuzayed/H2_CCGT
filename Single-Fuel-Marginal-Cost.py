# -*- coding: utf-8 -*-
"""
@author: Anas Abuzayed © 2025
https://github.com/AnasAbuzayed/H2_CCGT

Description:
This script reproduces figure 2 All data used are cited in the main paper. 

"""


import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = 'browser'
import os 
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

createFolder('Figures')
df=pd.read_excel('Calculations.xlsx',sheet_name='Single Fuel_New')

df.set_index('Route', inplace=True)

cost_components = ['Production', 'Synthesis', 'Shipping', 'Delivery', 'Regasification', 'Cracking','Carbon']

df=df[cost_components]



df[['Production', 'Synthesis', 'Shipping', 'Delivery', 'Regasification', 'Cracking']]/=0.63


grouped = df.groupby('Route')
mean_components = grouped[cost_components].mean()
# mean_components=mean_components.loc[mean_components.sum(axis=1).sort_values().index]

df['Total_cost'] = df[cost_components].sum(axis=1)
mean_total = grouped['Total_cost'].mean()

# mean_total=mean_total.loc[mean_components.sum(axis=1).sort_values().index]

min_total = grouped['Total_cost'].min()*0.8
error_lower = mean_total - min_total

max_total = grouped['Total_cost'].max()*1.2
error_upper = max_total - mean_total

sorted_routes = mean_total.sort_values().index

# Reorder dataframes accordingly
mean_components = mean_components.loc[sorted_routes]
mean_total = mean_total.loc[sorted_routes]
min_total = min_total.loc[sorted_routes]
max_total = max_total.loc[sorted_routes]
error_lower = error_lower.loc[sorted_routes]
error_upper = error_upper.loc[sorted_routes]


colors = {
    'Production': '#1f77b4',      
    'Synthesis': '#ff7f0e',      
    'Shipping': '#2ca02c',       
    'Delivery': '#d35050',        
    'Storage': '#9467bd',         
    'Regasification': '#b8ea04',  
    'Cracking': '#e377c2',        
    'Fuel cost': '#17becf',       
    'Carbon': '#7f6a4d'           
}



 
bars = []
routes = mean_components.index.tolist()

route_to_num = {route: i for i, route in enumerate(routes)}
x_numeric = list(route_to_num.values())

# Add stacked bars for each component
for component in cost_components:
    bars.append(go.Bar(
        x=x_numeric,
        y=mean_components[component],
        name=component,
        marker_color=colors.get(component, 'gray'),
        text=mean_components[component].round(0),
        textposition=['inside' for val in df[component]],
    ))

error_trace = go.Scatter(
    x=[x + 0.3 for x in x_numeric],
    y=mean_total,
    mode='markers',
    marker=dict(color='rgba(0,0,0,0)'),
    error_y=dict(
        type='data',
        symmetric=False,
        array=error_upper,
        arrayminus=error_lower,
        thickness=3,
        width=8,
        color='black'
    ),
    showlegend=False,
    hoverinfo='skip'
)

fig = go.Figure(data=bars + [error_trace])

fig.update_layout(
    barmode='stack',
    legend=dict(
        font=dict(size=24)  # legend font size here
    ),

    # title='Breakdown of marginal cost of electricity',
    yaxis_title='Marginal cost of electricity (€/MWh)',
    legend_title='Cost Components',
    height=900,
    font=dict(color="black", size=22),  # default font size for axis labels and ticks
    xaxis=dict(tickangle=45, tickfont=dict(size=22)),  # x-axis tick font size
    yaxis=dict(tickfont=dict(size=22)),  # y-axis tick font size
    width=2000
)





annotations = []

for idx,route in enumerate(routes):
    x_pos = x_numeric[idx]
    y_top = max_total[route]
    y_mean = mean_total[route]
    y_min = min_total[route]

    # Show max value above the top of the error bar
    annotations.append(dict(
        x=x_pos+0.35,
        y=y_top + 5,  # a bit above max error bar for clarity
        text=f"Max: {y_top:.0f}",
        showarrow=False,
        bgcolor='rgba(255, 215, 0, 0.5)',
        font=dict(color="black", size=16),
        align="center",xshift=5
    ))

    # Optionally, show min value below the bottom error bar
    annotations.append(dict(
        x=x_pos+0.35,
        y=y_min - 5,  # a bit below min error bar
        text=f"Min: {y_min:.0f}",
        bgcolor='rgba(255, 215, 0, 0.5)',
        showarrow=False,
        font=dict(color="black", size=16),
        align="center",
    ))

    # Or show the range or mean if you prefer instead


fig.update_layout(
    xaxis_tickangle=0,
    xaxis=dict(
        tickmode='array',
        tickvals=x_numeric,
        ticktext=[r.replace(' ', '<br>') for r in routes]
    )
)

# Add annotations to layout
fig.update_layout(annotations=annotations)


fig.write_image("Figures/cost_components_breakdown.png",scale=2)

fig.show()


