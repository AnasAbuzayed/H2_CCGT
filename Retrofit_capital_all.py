# -*- coding: utf-8 -*-
"""
@author: Anas Abuzayed © 2025
https://github.com/AnasAbuzayed/H2_CCGT

Description:
This script reproduces figure 6 All data used are cited in the main paper. 

"""





import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
pio.renderers.default = 'browser'
import os 
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

createFolder('Figures')

df=pd.read_excel('Calculations.xlsx',sheet_name='UK',
                  index_col=0,usecols=range(7),nrows=19)

df/=1e9
# temp=df['CCGT Investment Cost'].mean()

df.drop(['CCGT Investment Cost'],axis=1,inplace=True)
df=df[['Retrofit Investment','H2-Storage tank', 'H2-Storage salt cavern', 'NH3-Storage',
        'CH4-Storage']]


# df.loc['CCGT Fleet','CCGT Investment Cost']=temp

cost_components=df.columns

colors = {
    'H2-Storage tank': '#1f77b4',      
    'H2-Storage salt cavern': '#ff7f0e',      
    'NH3-Storage': '#2ca02c',       
    'CH4-Storage': '#d35050',        
    'Retrofit Investment': '#9467bd',         
    'CCGT Investment Cost': '#e377c2',        
}



single_idxs = df.index[:6]
binary_idxs = df.index[6:14]
ternary_idxs = df.index[14:]

def sort_group(df_group):
    return df_group.assign(Total=df_group.sum(axis=1)).sort_values(by='Total', ascending=True).drop(columns='Total')

df_single_sorted = sort_group(df.loc[single_idxs])
df_binary_sorted = sort_group(df.loc[binary_idxs])
df_ternary_sorted = sort_group(df.loc[ternary_idxs])

df_sorted = pd.concat([df_single_sorted, df_binary_sorted, df_ternary_sorted])

routes = df_sorted.index.tolist()
n = len(routes)

# 2. Dashed tilted dividing lines between groups
dividers = [5.5, 13.5]

def index_to_paper_coord(idx, total):
    return (idx + 0.5) / total

shapes = []
for idx in dividers:
    x_center = index_to_paper_coord(idx, n)
    offset = 0.01  # tilt offset

    # Vertical dashed line down to x-axis
    shapes.append(dict(
        type='line',
        xref='paper',
        yref='paper',
        x0=x_center,
        x1=x_center,
        y0=0,
        y1=1.0,
        line=dict(color='black', width=4, dash='dash')
    ))

    # Tilted dashed legs below x-axis
    shapes.append(dict(
        type='line',
        xref='paper',
        yref='paper',
        x0=x_center ,
        x1=x_center + 12.7*offset,
        y0=0,
        y1=-0.4,
        line=dict(color='black', width=4, dash='dash')
    ))

# 3. Group labels inside the plot at y=250
annotations = []
groups = [
    (0, 4, 'Single'),
    (5, 12, 'Binary'),
    (13, 17, 'Ternary')
]

for start, end, label in groups:
    center_idx = (start + end) // 2
    x_label = routes[center_idx]
    annotations.append(dict(
        x=x_label,
        y=15,
        xref='x',
        yref='y',
        text=f"<b>{label}</b>",
        showarrow=False,
        font=dict(size=22, color='black'),
        align='center',
        # bgcolor='white',
        # bordercolor='black',
        # borderwidth=1,
        # opacity=0.8
    ))

# 4. Build stacked bar traces
bars = []
for component in df_sorted.columns:
    bars.append(go.Bar(
        x=routes,
        y=df_sorted[component],
        name=component,
        marker_color=colors.get(component, 'gray'),
        text=[f"{val:.1f}" if val > 0 else "" for val in df_sorted[component]],
        textposition=['inside' if val > 0 else 'outside' for val in df_sorted[component]],
        textfont=dict(size=17)
    ))

# 5. Add total value annotations on top of each stacked bar
totals = df_sorted.sum(axis=1)
for route, total in zip(routes, totals):
    annotations.append(dict(
        x=route,
        y=total + 0.3,  # Slightly above the bar
        xref='x',
        yref='y',
        text=f"<b>{total:.1f}</b>",
        showarrow=False,
        font=dict(size=18, color='black'),
        align='center',
        # bgcolor='white',
        # bordercolor='black',
        # borderwidth=1,
        # opacity=0.9
    ))

# 6. Create figure
fig = go.Figure(data=bars)
fig.update_layout(
    barmode='stack',
    title=dict(
        text='Breakdown of total investment cost for the UK',
        font=dict(size=32, family='Arial Black')),
    yaxis_title=dict(text='Total investment cost (Billion €)',
                     font=dict(size=22,family='Arial Black')),
    legend_title='Cost Components',
    legend=dict(
        font=dict(size=22)  # legend font size here
    ),

    height=900,
    width=2000,
    shapes=shapes,
    annotations=annotations,
    xaxis=dict(tickangle=45, tickfont=dict(size=22)),  # x-axis tick font size
    yaxis=dict(tickfont=dict(size=26)),  # y-axis tick font size

)

# 
fig.write_image("Figures/UK_capital_components_breakdown_all.png",scale=2)

fig.show()















# # # ###### Germany





df=pd.read_excel('Calculations.xlsx',sheet_name='DE',
                  index_col=0,usecols=range(7),nrows=19)

df/=1e9
# temp=df['CCGT Investment Cost'].mean()

df.drop(['CCGT Investment Cost'],axis=1,inplace=True)
df=df[['Retrofit Investment','H2-Storage tank', 'H2-Storage salt cavern', 'NH3-Storage',
       'CH4-Storage']]


# df.loc['CCGT Fleet','CCGT Investment Cost']=temp

cost_components=df.columns

colors = {
    'H2-Storage tank': '#1f77b4',      
    'H2-Storage salt cavern': '#ff7f0e',      
    'NH3-Storage': '#2ca02c',       
    'CH4-Storage': '#d35050',        
    'Retrofit Investment': '#9467bd',         
    'CCGT Investment Cost': '#e377c2',        
}



single_idxs = df.index[:6]
binary_idxs = df.index[6:14]
ternary_idxs = df.index[14:]

def sort_group(df_group):
    return df_group.assign(Total=df_group.sum(axis=1)).sort_values(by='Total', ascending=True).drop(columns='Total')

df_single_sorted = sort_group(df.loc[single_idxs])
df_binary_sorted = sort_group(df.loc[binary_idxs])
df_ternary_sorted = sort_group(df.loc[ternary_idxs])

df_sorted = pd.concat([df_single_sorted, df_binary_sorted, df_ternary_sorted])

routes = df_sorted.index.tolist()
n = len(routes)

# 2. Dashed tilted dividing lines between groups
dividers = [5.5, 13.5]

def index_to_paper_coord(idx, total):
    return (idx + 0.5) / total

shapes = []
for idx in dividers:
    x_center = index_to_paper_coord(idx, n)
    offset = 0.01  # tilt offset

    # Vertical dashed line down to x-axis
    shapes.append(dict(
        type='line',
        xref='paper',
        yref='paper',
        x0=x_center,
        x1=x_center,
        y0=0,
        y1=1.0,
        line=dict(color='black', width=4, dash='dash')
    ))

    # Tilted dashed legs below x-axis
    shapes.append(dict(
        type='line',
        xref='paper',
        yref='paper',
        x0=x_center ,
        x1=x_center + 12.7*offset,
        y0=0,
        y1=-0.4,
        line=dict(color='black', width=4, dash='dash')
    ))

# 3. Group labels inside the plot at y=250
annotations = []
groups = [
    (0, 4, 'Single'),
    (5, 12, 'Binary'),
    (13, 17, 'Ternary')
]

for start, end, label in groups:
    center_idx = (start + end) // 2
    x_label = routes[center_idx]
    annotations.append(dict(
        x=x_label,
        y=20,
        xref='x',
        yref='y',
        text=f"<b>{label}</b>",
        showarrow=False,
        font=dict(size=22, color='black'),
        align='center',
        # bgcolor='white',
        # bordercolor='black',
        # borderwidth=1,
        # opacity=0.8
    ))

# 4. Build stacked bar traces
bars = []
for component in df_sorted.columns:
    bars.append(go.Bar(
        x=routes,
        y=df_sorted[component],
        name=component,
        marker_color=colors.get(component, 'gray'),
        text=[f"{val:.1f}" if val > 0 else "" for val in df_sorted[component]],
        textposition=['inside' if val > 0 else 'outside' for val in df_sorted[component]],
        textfont=dict(size=17)
    ))

# 5. Add total value annotations on top of each stacked bar
totals = df_sorted.sum(axis=1)
for route, total in zip(routes, totals):
    annotations.append(dict(
        x=route,
        y=total + 0.3,  # Slightly above the bar
        xref='x',
        yref='y',
        text=f"<b>{total:.1f}</b>",
        showarrow=False,
        font=dict(size=18, color='black'),
        align='center',
        # bgcolor='white',
        # bordercolor='black',
        # borderwidth=1,
        # opacity=0.9
    ))

# 6. Create figure
fig = go.Figure(data=bars)
fig.update_layout(
    barmode='stack',
    title=dict(
        text='Breakdown of total investment cost for Germany',
        font=dict(size=32, family='Arial Black')),
    yaxis_title=dict(text='Total investment cost (Billion €)',
                     font=dict(size=22,family='Arial Black')),
    legend_title='Cost Components',
    legend=dict(
        font=dict(size=22)  # legend font size here
    ),

    height=900,
    width=2000,
    shapes=shapes,
    annotations=annotations,
    xaxis=dict(tickangle=45, tickfont=dict(size=22)),  # x-axis tick font size
    yaxis=dict(tickfont=dict(size=26)),  # y-axis tick font size

)

# 
fig.write_image("Figures/DE_capital_components_breakdown_all.png",scale=2)

fig.show()


