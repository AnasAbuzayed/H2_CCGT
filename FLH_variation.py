# -*- coding: utf-8 -*-
"""
@author: Anas Abuzayed © 2025
https://github.com/AnasAbuzayed/H2_CCGT

Description:
This script reproduces figure A3 All data used are cited in the main paper. 

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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
E = FLH * capacity  # Annual energy output (MWh)

# Storage CAPEX (EUR/MWh_fuel)
H2_capex = 1091.02  #Storage Tank
NH3_capex = 157.64 
CH4_capex = 182.07 

FOM_storage = 0.02
days = 3
reserve = (days * capacity * 24 / 1e3) / efficiency  # MWh_fuel

def get_retrofit_cost(f1):
    if f1 == 'Hydrogen Tank' or f1 == 'Hydrogen Cavern' or f1 == 'Ammonia Cracking':
        return 0.0798
    if f1 == 'Ammonia':
        return 0.1134
    else:
        return 0


# LCOE function
def lcoe(E,retrofit_pct):
    initial =capacity * (capex*(1+retrofit_pct)) * (1 + fcr_p) 
    money = sum((FOM * capacity + E * VOM / 1000) / ((1 + WACC) ** y) for y in range(1, CCGT_lifetime + 1))
    energy = sum(E / ((1 + WACC) ** y) for y in range(1, CCGT_lifetime + 1))
    return (initial + money) / energy * 1000


# LCOS function
def lcos(reserve, CAPEX):
    initial = reserve  * (CAPEX) * (1 + fcr_s) 
    money = sum((FOM_storage * initial) / ((1 + WACC) ** y) for y in range(1, storage_lifetime + 1))
    energy = sum(E / ((1 + WACC) ** y) for y in range(1, storage_lifetime + 1))
    return (initial + money) / energy * 1000





# Fuel definitions
fuels=['Hydrogen Tank','Hydrogen Cavern','Ammonia Cracking','Ammonia','Biomethane']
costs=[1091.02,321.86,157.64,157.64,182.07]


fuels_cost=pd.DataFrame({'CAPEX':costs},index=fuels)






# # Fuel combinations to evaluate

# df_results=pd.DataFrame(0,index=range(100,3001,1),columns=fuels)



# for tech in df_results.columns:
#     for FLH in range(100,3001,1):
#         E = FLH * capacity  # Annual energy output (MWh)      
#         retrofit_pct = get_retrofit_cost(tech)
#         df_results.loc[FLH,tech]=lcoe(E,retrofit_pct) + lcos(reserve,fuels_cost.loc[tech,'CAPEX'])






# fig, ax = plt.subplots(figsize=(12,6))
# ax.tick_params(axis='both', which='major', labelsize=11)
# ax.set_ylabel("Levelized cost of electricity (€/MWh)",fontsize=18)
# df_results.plot(ax=ax)
# ax.grid()
# ax.set_yticks([0,25,50,75,100,200,400,600,800,1000])
# fig.tight_layout(pad=2)
# ax.set_title(label='LCOE variation with FLH',fontsize=22)
# ax.set_xlabel('Hour',fontsize=18)
# ax.legend(fontsize=15)
# plt.savefig('Figures/LCOE - FLH',dpi=300)






# FLH=1000
# E = FLH * capacity  # Annual energy output (MWh)      
# df_results=pd.DataFrame(0,index=range(1,22,1),columns=fuels)

# for tech in df_results.columns:
#     for day in range(1,22,1):
#         reserve = (day * capacity * 24 / 1e3) / efficiency  # MWh_fuel
#         retrofit_pct = get_retrofit_cost(tech)

#         df_results.loc[day,tech]=lcoe(E,retrofit_pct) + lcos(reserve,fuels_cost.loc[tech,'CAPEX'])








# fig, ax = plt.subplots(figsize=(16,9))
# ax.tick_params(axis='both', which='major', labelsize=11)
# ax.set_ylabel("Levelized cost of electricity (€/MWh)",fontsize=18)
# df_results.plot(ax=ax)
# ax.grid()
# ax.set_yticks(range(90,201,10))
# ax.set_xticks(range(1,22,1))
# fig.tight_layout(pad=2)
# ax.set_title(label='LCOE variation with reserve days',fontsize=22)
# ax.set_xlabel('Day',fontsize=18)
# ax.legend(fontsize=15)
# plt.savefig('Figures/LCOE - reserve',dpi=300)




FLH_range = range(100, 3001, 100)   
day_range = range(1, 22)          
results = []

# Loop over combinations
for tech in fuels:
    retrofit_pct = get_retrofit_cost(tech)
    for FLH in FLH_range:
        for day in day_range:
            E = FLH * capacity  # MWh/year
            reserve = (day * capacity * 24 / 1e3) / efficiency  # MWh_fuel
            val = lcoe(E,retrofit_pct) + lcos(reserve, fuels_cost.loc[tech, 'CAPEX'])

            # Store results in a dict
            results.append({
                'FLH': FLH,
                'days': day,
                'tech': tech,
                'value': val,
                'firing': lcoe(E,retrofit_pct),
                'storage': lcos(reserve, fuels_cost.loc[tech, 'CAPEX'])
            })

df_results = pd.DataFrame(results)






z=-1
fig, axs = plt.subplots(2,3,figsize=(28,14))
for i in axs:
    for j in i:
        z+=1
        if z==5:
            break     
        df_tech=df_results[df_results['tech'] == fuels[z]]
        
        sns.lineplot(data=df_tech, 
                     x='FLH', y='value', hue='days',
                     ax=j,lw=1,dashes=True,
                     palette='viridis')

        j.set_xlabel("Full Load Hours (FLH)", fontsize=16)  # x-axis label font size
        j.set_ylabel("LCOE (EUR/MWh)", fontsize=16)  # y-axis label font size

        j.set_title(label=f'{fuels[z]}',fontsize=22)
        j.grid(True)
        j.legend(fontsize=12)

        j.set_yticks(range(0,2001,100))

plt.tight_layout()
axs[1][2].axis('off')
plt.savefig('Figures/LCOE - FLH-reserve',dpi=300)








# df_tech = df_results[df_results['tech'] == 'Hydrogen Tank']

# fig, ax1 = plt.subplots(figsize=(10,6))

# # Plot FLH on left y-axis vs LCOE (value)
# color1 = 'tab:blue'
# ax1.scatter(df_tech['FLH'], df_tech['value'], color=color1, label='FLH')
# ax1.set_xlabel('LCOE (EUR/MWh)')
# ax1.set_ylabel('FLH', color=color1)
# ax1.tick_params(axis='y', labelcolor=color1)

# # Create second y-axis sharing the same x-axis
# ax2 = ax1.twinx()
# color2 = 'tab:orange'
# ax2.scatter(df_tech['value'], df_tech['days'], color=color2, label='Days')
# ax2.set_ylabel('Days', color=color2)
# ax2.tick_params(axis='y', labelcolor=color2)

# plt.title(f'FLH and Days vs LCOE for Hydrogen Tank')
# fig.tight_layout()
# plt.show()

