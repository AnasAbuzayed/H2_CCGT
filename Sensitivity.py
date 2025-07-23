# -*- coding: utf-8 -*-
"""
@author: Anas Abuzayed © 2025
https://github.com/AnasAbuzayed/H2_CCGT

Description:
This script reproduces figures A1-A2 All data used are cited in the main paper. 

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import itertools
import inspect
import os 
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

createFolder('Figures')
# Constants
efficiency = 0.63
capex = 1039.34 # EUR/kW CCGT
capacity = 38e6  # 38 GW
FOM = 14  # EUR/kW/year
VOM = 3  # EUR/MWh
FLH = 1000  # Full-load hours
fcr_p = 0.08083586
fcr_s = 0.102880385
WACC = 0.0581
storage_lifetime = 20
CCGT_lifetime = 35

# Storage CAPEX (EUR/MWh_fuel)
store_capex = {
    "H2-Tank": {"capex": 1091.02 },
    "H2-Cavern": {"capex": 321.86},
    "NH3": {"capex": 157.64 },
    "CH4": {"capex": 182.07 },
    "NH3c": {"capex": 157.64 },
}

FOM_storage = 0.02
days = 3


# LCOE function
def lcoe(E,retrofit_pct):
    initial =capacity * (capex*(1+retrofit_pct)) * (1 + fcr_p) 
    money = sum((FOM * capacity + E * VOM / 1000) / ((1 + WACC) ** y) for y in range(1, CCGT_lifetime + 1))
    energy = sum(E / ((1 + WACC) ** y) for y in range(1, CCGT_lifetime + 1))
    return (initial + money) / energy * 1000


# LCOS function
def lcos(E,reserve, CAPEX):
    initial = reserve  * CAPEX * (1 + fcr_s) 
    money = sum((FOM_storage * initial) / ((1 + WACC) ** y) for y in range(1, storage_lifetime + 1))
    energy = sum(E / ((1 + WACC) ** y) for y in range(1, storage_lifetime + 1))
    return (initial + money) / energy * 1000

def get_retrofit_cost(f1):
    if f1 == 'H2-Tank' or f1 == 'H2-Cavern' or f1 == 'NH3c':
        return 0.0798
    if f1 == 'NH3':
        return 0.1134
    else:
        return 0


fuels=pd.DataFrame(0,index=store_capex.keys(),columns=['Production', 'Synthesis', 'Shipping','Distribution','Regasification'])

fuels.loc['H2-Tank']=[49.48 , 9.58 , 24.26 , 22.72 , 8.47]
fuels.loc['H2-Cavern']=[49.48 , 9.58 , 24.26 , 22.72 , 8.47]
fuels.loc['NH3']=[49.48 , 34 , 9.08 , 3.44 ,0 ]
fuels.loc['NH3c']=[49.48 , 34 , 9.08 , 3.44 ,0 ]
fuels.loc['CH4']=[97.19,0,0,4.71,0]

fuels['Cracking']=0

fuels.loc['NH3c','Cracking']=fuels.loc['NH3'].sum()*0.2












def run_lcoe_analysis(capex, FOM, VOM, FLH,
                      FOM_storage, days, store,Retrofit):

    capacity = 38e6
    E = FLH * capacity
    reserve = (days * capacity * 24 / 1e3) / efficiency
    
    def lcoe(E,retrofit_pct):
        initial =capacity * (capex*(1+retrofit_pct)) * (1 + fcr_p) 
        money = sum((FOM * capacity + E * VOM / 1000) / ((1 + WACC) ** y) for y in range(1, 35 + 1))
        energy = sum(E / ((1 + WACC) ** y) for y in range(1, 35 + 1))
        return (initial + money) / energy * 1000

    def lcos(E,reserve, CAPEX):
        initial = reserve * CAPEX * (1 + fcr_s) 
        money = sum((FOM_storage * initial) / ((1 + WACC) ** y) for y in range(1, storage_lifetime + 1))
        energy = sum(E / ((1 + WACC) ** y) for y in range(1, storage_lifetime + 1))
        return (initial + money) / energy * 1000

    fuels_copy = fuels.copy()
    
    for fuel in fuels_copy.index:
        fuels_copy.loc[fuel,'Storage'] = lcos(E, reserve, store_capex[fuel]['capex'] * (store))
        fuels_copy.loc[fuel,'Firing'] = lcoe(E, get_retrofit_cost(fuel) * (Retrofit))

    fuels_copy['LCOE'] =  fuels_copy['Storage'] + fuels_copy['Firing']
    
    
    return fuels_copy['LCOE']

# Baseline values
baseline_LCOE= run_lcoe_analysis(capex, FOM, VOM, FLH,
                      FOM_storage, days, store=1,Retrofit=1)



# Sensitivity parameters
params = {
    'capex':capex,
    'FOM':FOM,
    'VOM':VOM,
    'FLH':FLH,
    'FOM_storage':FOM_storage,
    'days': days,
    'store':1,
    'Retrofit':1,
}




LCOE_sensitivity_results = []

# Range: ±2% to ±20%
percentage_changes = np.arange(-0.2, 0.21, 0.02)

for param, base_value in params.items():
    for pct_change in percentage_changes:

        new_value = base_value * (1 + pct_change)
        param_values = params.copy()
        
#        if param =='days':
 #           new_value = base_value * (1 + pct_change)
  #          new_value = 3 + (pct_change * 10)  # between 1 and 5 days

     
        param_values[param] = new_value

        lcoe_values = run_lcoe_analysis(
            param_values['capex'], 
            param_values['FOM'], 
            param_values['VOM'], 
            param_values['FLH'],
            param_values['FOM_storage'], 
            param_values['days'], 
            param_values['store'], 
            param_values['Retrofit'])
        for fuel in lcoe_values.index:
            delta = (lcoe_values[fuel] - baseline_LCOE[fuel])
            LCOE_sensitivity_results.append({
                'Parameter': param,
                'Change (%)': pct_change * 100,
                'Fuel': fuel,
                'ΔLCOE (EUR/MWh)': delta
            })


# Create DataFrame
sensitivity_df = pd.DataFrame(LCOE_sensitivity_results)
sensitivity_df.Parameter.replace('capex','CCGT CAPEX',inplace=True)
sensitivity_df.Parameter.replace('store','Storage CAPEX',inplace=True)




color_dict = {
    'efficiency':      '#1f77b4',  # Blue
    'CCGT CAPEX':      '#d62728',  # Red
    'FOM':             '#2ca02c',  # Green
    'VOM':             '#9467bd',  # Purple
    'FLH':             '#ff7f0e',  # Orange
    'FOM_storage':     '#8c564b',  # Brown
    'Storage CAPEX':   '#17becf',  # Teal
    'Retrofit':   '#bcbd22',  
    'days':            'fuchsia',  # Pink
    'retrofit_pct':    '#7f7f7f',  # Gray
    'Production':      '#bcbd22',  # Yellow-green
    'Synthesis':       '#1a55FF',  # Vivid Blue
    'Shipping':        '#b8ea04',  # Deep Pink
    'Distribution':    '#FFD700',  
    'Regasification':  'fuchsia', 
    'Cracking':        'limegreen' 
}


z=-1
fig, axs = plt.subplots(2,3,figsize=(40,20))
for i in axs:
    for j in i:
        z+=1
        if z==5:
            break        
        sns.lineplot(data=sensitivity_df[sensitivity_df['Fuel'] == sensitivity_df.Fuel.unique()[z]], 
                     x='Change (%)', y='ΔLCOE (EUR/MWh)', hue='Parameter',
                     ax=j,lw=4,dashes=True,
                     palette=color_dict)
        j.set_xlabel("Change in parameter (%)", fontsize=16)  # x-axis label font size
        j.set_ylabel("Change in LCOE (%)", fontsize=16)  # y-axis label font size

        j.set_title(label=f'LCOE Sensitivity for {sensitivity_df.Fuel.unique()[z]}',fontsize=22)
        j.axhline(0, color='gray', linestyle='--')
        j.grid(True)
        handles, labels = j.get_legend_handles_labels()
        j.legend("")
        j.set_yticks(range(-20,31,5))


for h in handles:
    h.set_linewidth(4)
axs[1][2].legend(handles=handles, labels=labels, ncol=3,
             loc='center', fontsize=24, title='Parameter', title_fontsize=28)
axs[1][2].axis('off')
plt.tight_layout()
plt.savefig('Figures/LCOE-Sensitivity All',dpi=220)













fuels=pd.DataFrame(0,index=['H2-Global','NH3-Global','NH3c-Global',
                            'CH4','H2-Local','NH3-Local','NH3c-Local'],
                   columns=['Production', 'Synthesis', 'Shipping'
                            ,'Distribution','Regasification'])

fuels.loc['H2-Global']=[49.48 , 9.58 , 24.26 , 22.72 , 8.47]
fuels.loc['NH3-Global']=[49.48 , 34 , 9.08 , 3.44 ,0]
fuels.loc['CH4']=[97.19,0,0,4.71,0]
fuels.loc['NH3c-Global']=fuels.loc['NH3-Global']

fuels.loc['H2-Local']=[86.1 , 9.58 , 0, 22.72 , 8.47]
fuels.loc['NH3-Local']=[86.1 , 34 , 0, 3.44, 0]
fuels.loc['NH3c-Local']=fuels.loc['NH3-Local']

fuels['Cracking']=0

fuels.loc['NH3c-Global','Cracking']=fuels.loc['NH3c-Global'].sum()*0.2
fuels.loc['NH3c-Local','Cracking']=fuels.loc['NH3c-Local'].sum()*0.2





def run_mcoe_analysis(Production,Synthesis, Shipping, 
                      Distribution, Regasification, Cracking):


    fuels_copy = fuels.copy()
    
    fuels_copy.Production= Production
    fuels_copy.Synthesis= Synthesis
    fuels_copy.Shipping= Shipping
    fuels_copy.Distribution= Distribution
    fuels_copy.Regasification= Regasification
    fuels_copy.Cracking= Cracking

    fuels_copy['Marginal Cost']=fuels_copy.sum(axis=1)/0.63

    
    return fuels_copy['Marginal Cost']




MCOE_sensitivity_results = []

baseline_MCOE = run_mcoe_analysis(
                      Production = fuels.Production,
                      Synthesis=fuels.Synthesis,
                      Shipping=fuels.Shipping,
                      Distribution=fuels.Distribution,
                      Regasification=fuels.Regasification,
                      Cracking=fuels.Cracking)



# Sensitivity parameters
params = {
    'Production' : fuels.Production,
    'Synthesis': fuels.Synthesis,
    'Shipping': fuels.Shipping,
    'Distribution': fuels.Distribution,
    'Regasification': fuels.Regasification,
    'Cracking' : fuels.Cracking
}




MCOE_sensitivity_results = []

# Range: ±2% to ±20%
percentage_changes = np.arange(-0.2, 0.21, 0.02)

for param, base_value in params.items():
    for pct_change in percentage_changes:
        new_value = base_value * (1 + pct_change)
        param_values = params.copy()
        param_values[param] = new_value

        mcoe_values = run_mcoe_analysis(
            param_values['Production'],
            param_values['Synthesis'],
            param_values['Shipping'],
            param_values['Distribution'],
            param_values['Regasification'],
            param_values['Cracking'])

        for fuel in mcoe_values.index:
            delta = (mcoe_values[fuel] - baseline_MCOE[fuel])
            MCOE_sensitivity_results.append({
                'Parameter': param,
                'Change (%)': pct_change * 100,
                'Fuel': fuel,
                'ΔLCOE (EUR/MWh)': delta
            })

sensitivity_df = pd.DataFrame(MCOE_sensitivity_results)




color_dict = {
    'efficiency':      '#1f77b4',  # Blue
    'CCGT CAPEX':      '#d62728',  # Red
    'FOM':             '#2ca02c',  # Green
    'VOM':             '#9467bd',  # Purple
    'FLH':             '#ff7f0e',  # Orange
    'FOM_storage':     '#8c564b',  # Brown
    'Storage CAPEX':   '#17becf',  # Teal
    'Retrofit':   'k',  
    'days':            '#e377c2',  # Pink
    'retrofit_pct':    '#7f7f7f',  # Gray
    'Production':      '#17becf',  # Yellow-green
    'Synthesis':       '#1a55FF',  # Vivid Blue
    'Shipping':        '#b8ea04',  # Deep Pink
    'Distribution':    '#ff7f0e',  
    'Regasification':  'fuchsia', 
    'Cracking':        '#7f7f7f' 
}


z=-1
fig, axs = plt.subplots(3,3,figsize=(40,20))
for i in axs:
    for j in i:
        z+=1
        if z==7:
            break        
        sns.lineplot(data=sensitivity_df[sensitivity_df['Fuel'] == sensitivity_df.Fuel.unique()[z]], 
                     x='Change (%)', y='ΔLCOE (EUR/MWh)', hue='Parameter',
                     ax=j,lw=4,dashes=True,
                     palette=color_dict)
        j.set_xlabel("Change in parameter (%)", fontsize=16)  # x-axis label font size
        j.set_ylabel("Change in MCOE (%)", fontsize=16)  # y-axis label font size

        j.set_title(label=f'MCOE Sensitivity for {sensitivity_df.Fuel.unique()[z]}',fontsize=22)
        j.axhline(0, color='gray', linestyle='--')
        j.grid(True)
        handles, labels = j.get_legend_handles_labels()
        j.legend("")
        j.set_yticks(range(-30,31,5))


for h in handles:
    h.set_linewidth(4)
axs[2][1].legend(handles=handles, labels=labels, ncol=3,
             loc='center', fontsize=24, title='Parameter', title_fontsize=28)
axs[2][2].axis('off')
axs[2][1].axis('off')
plt.tight_layout()
plt.savefig('Figures/MCOE-Sensitivity All',dpi=220)

