# -*- coding: utf-8 -*-
"""
@author: Anas Abuzayed © 2025
https://github.com/AnasAbuzayed/H2_CCGT

Description:
This script reproduces figure 3 All data used are cited in the main paper. 

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
df=pd.read_excel('Calculations.xlsx',sheet_name='Firing Comparison')

df.set_index('Route', inplace=True)
df.index

df['CCGT Investment Cost']=df.loc['Biomethane','CCGT Investment Cost']

colors = {
    'CCGT Investment Cost': '#1f77b4',      
    'Storage': '#ff7f0e',      
    'Retrofitting': '#2ca02c',       
}


df.loc['Binary Combustion','Storage']=df.Storage.max()
df.loc['Ternary Combustion','Storage']=df.Storage.max()


routes = df.index.tolist()
route_to_num = {route: i for i, route in enumerate(routes)}
x_numeric = list(route_to_num.values())



bars = []
routes = df.index.tolist()

# Add stacked bars for each component
for component in df.columns:
    bars.append(go.Bar(
        x=routes,
        y=df[component],
        name=component,
        marker_color=colors.get(component, 'gray'),
        text=df[component].round(1),
        textposition=['inside' if val > 5 else 'outside' for val in df[component]],

    ))


fig = go.Figure(data=bars)
fig.update_layout(
    barmode='stack',
    # title='LCOE of CCGT - Breakdown of single-firing',
    yaxis_title='LCOE of investment (€/MWh)',
    legend_title='Cost Components',
    height=900,
    font=dict(color="black", size=22),  # default font size for axis labels and ticks
    xaxis=dict(tickangle=45, tickfont=dict(size=22)),  # x-axis tick font size
    yaxis=dict(tickfont=dict(size=22)),  # y-axis tick font size
    width=2000
)

y_base = df.loc['Ternary Combustion', 'CCGT Investment Cost'] + df.loc['Ternary Combustion', 'Retrofitting']
y_min = y_base + 2.103483
y_max = y_base + 14.558037

# Add horizontal line segment at y_line
fig.add_shape(
    type="line",
    x0=x_numeric[-1] - 0.4,
    x1=x_numeric[-1] + 0.4,
    y0=y_min,
    y1=y_min,
    line=dict(color="fuchsia", width=3,dash='dashdot'),
    xref="x",
    yref="y",
)



arrow_x_pos=x_numeric [-1]+ 0.25

fig.add_annotation(
    x=arrow_x_pos,
    y=y_max,
    axref="x",
    ayref="y",
    ax=arrow_x_pos,
    ay=y_min,
    showarrow=True,
    arrowhead=2,
    arrowside="start+end",  # ←→ double arrow
    arrowwidth=1,
    arrowcolor="black",
    text="",  # No visible label
)


fig.add_annotation(
    x=x_numeric [-1]- 0.5,
    y=y_min,
    axref="x",
    ayref="y",
    ax=x_numeric [-1]- 0.5,
    ay=y_min,
    showarrow=False,
    text="2.1",  # No visible label
)



y_base = df.loc['Hydrogen (tank)','CCGT Investment Cost']
y_min = df.loc['Hydrogen (tank)','Retrofitting'] + y_base

# Add horizontal line segment at y_line
fig.add_shape(
    type="line",
    x0=x_numeric[-2] - 0.4,
    x1=x_numeric[-2] + 0.4,
    y0=y_min,
    y1=y_min,
    line=dict(color="fuchsia", width=3,dash='dashdot'),
    xref="x",
    yref="y",
)

y_base = df.loc['Binary Combustion',['CCGT Investment Cost','Retrofitting']].sum()
y_min = y_base+2.103483

fig.add_shape(
    type="line",
    x0=x_numeric[-2] - 0.4,
    x1=x_numeric[-2] + 0.4,
    y0=y_min,
    y1=y_min,
    line=dict(color="fuchsia", width=3,dash='dashdot'),
    xref="x",
    yref="y",
)



fig.add_annotation(
    x=x_numeric [-2]- 0.5,
    y=y_min,
    axref="x",
    ayref="y",
    ax=x_numeric [-1]- 0.5,
    ay=y_min,
    showarrow=False,
    text="2.1",  # No visible label
)




arrow_x_pos=x_numeric [-2]+ 0.25

fig.add_annotation(
    x=arrow_x_pos,
    y=df.loc['Binary Combustion'].sum(),
    axref="x",
    ayref="y",
    ax=arrow_x_pos,
    ay=y_min,
    showarrow=True,
    arrowhead=2,
    arrowside="start+end",  # ←→ double arrow
    arrowwidth=1,
    arrowcolor="black",
    text="",  # No visible label
)



y_base = df.loc['Binary Combustion',['CCGT Investment Cost','Retrofitting']].sum()
y_min = df.loc['Hydrogen (tank)',['CCGT Investment Cost','Retrofitting']].sum()



arrow_x_pos=x_numeric [-2]+ 0.25

fig.add_annotation(
    x=arrow_x_pos,
    y=y_base,
    axref="x",
    ayref="y",
    ax=arrow_x_pos,
    ay=y_min,
    showarrow=True,
    arrowhead=2,
    arrowside="start+end",  # ←→ double arrow
    arrowwidth=0.8,
    arrowcolor="black",
    text="",  # No visible label
)



fig.add_annotation(
    x=x_numeric [-2]- 0.5,
    y=y_min,
    axref="x",
    ayref="y",
    ax=x_numeric [-1]- 0.5,
    ay=y_min,
    showarrow=False,
    text="6",  # No visible label
)



fig.update_yaxes(
    range=[0, 140],       # y-axis limits
    dtick=20,             # tick interval (every 20)
    ticks="outside",      # show tick marks outside
    ticklen=5,
    tickwidth=1,
    tickcolor='black',
    tickfont=dict(size=22, color='black'),
    showgrid=True,
    gridcolor='lightgray'
)

fig.show()
fig.write_image("Figures/LCOE_components_breakdown.png",scale=4)
# 
# fig.write_image("LCOE_components_breakdown.pdf")

