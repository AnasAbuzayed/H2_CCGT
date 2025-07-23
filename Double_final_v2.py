# -*- coding: utf-8 -*-
"""
@author: Anas Abuzayed © 2025
https://github.com/AnasAbuzayed/H2_CCGT

Description:
This script reproduces figure 4 All data used are cited in the main paper. 

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

# Fuel costs (EUR/MWh_fuel)
H2_fuel_cost = 49.48 + 9.58 + 24.26 + 22.72 + 8.47 # Production + Liquefaction + shipping+distribution+regasification
NH3_fuel_cost = 49.48 + 34 + 9.08 + 3.44  # Production + Synthesis + shipping + distribution
NH3_cracking_fuel_cost = NH3_fuel_cost*1.2
CH4_fuel_cost = 97.19 + 4.71 # Production + Distribution

# Storage CAPEX (EUR/MWh_fuel)
H2_capex = 1091.02  * (1 + fcr_s) #Storage Tank
H2_cavern_capex = 321.02* (1 + fcr_s) #Storage Tank
NH3_capex = 157.64 * (1 + fcr_s) #Storage Tank
CH4_capex = 182.07 * (1 + fcr_s) #Storage Tank

FOM_storage = 0.02
days = 3
reserve = (days * capacity * 24 / 1e3) / efficiency  # MWh_fuel

# Compute annualized CAPEX + OPEX (used in all LCOE calculations)
money = energy = 0
for y in range(1, CCGT_lifetime + 1):
    df = (1 + WACC) ** y
    money += (FOM * capacity + E * VOM / 1000) / df
    energy += E / df

# LCOS function
def lcos(reserve, share, CAPEX):
    initial = reserve * share * CAPEX
    money = sum((FOM_storage * initial) / ((1 + WACC) ** y) for y in range(1, storage_lifetime + 1))
    energy = sum(E / ((1 + WACC) ** y) for y in range(1, storage_lifetime + 1))
    return (initial + money) / energy * 1000

# Fuel definitions
fuels = {
    "H2-cavern": {"cost": H2_fuel_cost, "capex": H2_cavern_capex},
    "H2-tank": {"cost": H2_fuel_cost, "capex": H2_capex},
    "NH3": {"cost": NH3_fuel_cost, "capex": NH3_capex},
    "CH4": {"cost": CH4_fuel_cost, "capex": CH4_capex},
    "NH3c": {"cost": NH3_cracking_fuel_cost, "capex": NH3_capex},
}


# Dynamic retrofit cost function
def get_retrofit_cost(f1, f2, X1):
    if f1== 'NH3' or f2=='NH3':
        return 0.1134
    else:        
        if f1== 'H2-cavern' or f2=='H2-cavern' or f1== 'H2-tank' or f2=='H2-tank':
            return 0.0798
        if f1== 'NH3c' or f2=='NH3c':
            return 0.0798



# Fuel combinations to evaluate
pairs = [("H2-cavern", "NH3"), ("H2-cavern", "CH4"), ("CH4", "NH3"),("CH4", "NH3c"),("H2-cavern", "NH3c"),
         ("H2-tank", "NH3"), ("H2-tank", "CH4"),("H2-tank", "NH3c")]
shares = np.linspace(0, 1, 1001)
all_results = []

for f1, f2 in pairs:
    for X1 in shares:
        X2 = 1 - X1
           
        # Fuel and storage costs
        fuel_cost = X1 * fuels[f1]["cost"] + X2 * fuels[f2]["cost"]
        lcos1 = lcos(reserve, X1, fuels[f1]["capex"])
        lcos2 = lcos(reserve, X2, fuels[f2]["capex"])


        # Retrofit and LCOE
        retrofit_pct = get_retrofit_cost(f1, f2, X1)
        firing = (capacity * capex * (1 + fcr_p) * (1 + retrofit_pct) + money) / energy * 1000
        LCOE = firing + lcos1 + lcos2


        
        all_results.append({
            "Blend": f"{f1}_{f2}",
            "Fuel1": f1,
            "Fuel2": f2,
            "PCT":retrofit_pct,
            "Fuel1_share": X1,
            "Fuel2_share": X2,
            "LCOE": LCOE,
            "Fuel_cost": fuel_cost / efficiency ,
            "LCOS": lcos1 + lcos2,
            "Firing": firing
        })
        

# Convert to DataFrame
df_all = pd.DataFrame(all_results)



LHV={'H2-tank':10.8,'H2-cavern':10.8,'NH3c':10.8,'NH3':12.7,'CH4':35}

def energy_to_volume_share(X_E, LHV1, LHV2):
    # Converts energy share to volumetric share
    if X_E == 0:
        return 0
    elif X_E == 1:
        return 1
    return (X_E * LHV2) / (LHV1 * (1 - X_E) + X_E * LHV2)

# Assume you have your dataframe called df (with Fuel1, Fuel2, Fuel1_share (energy))
# and LHV

vol_shares_1 = []
vol_shares_2 = []

for _, row in df_all.iterrows():
    f1, f2 = row['Fuel1'], row['Fuel2']
    X_E1 = row['Fuel1_share']  # energy share
    X_V1 = energy_to_volume_share(X_E1, LHV[f1], LHV[f2])
    X_V2 = 1 - X_V1
    vol_shares_1.append(X_V1)
    vol_shares_2.append(X_V2)

df_all['Fuel1_vol_share'] = vol_shares_1
df_all['Fuel2_vol_share'] = vol_shares_2






styles=['-.','--',':','-.',(0, (3, 5, 1, 5)),
        (0, (5, 1)), (0, (1, 1)), (0, (5, 10))]

# Plot: LCOE vs. Fuel 1 Share Energy & Vol
plt.figure(figsize=(10, 6))
sns.set_style("whitegrid")

for idx, blend in enumerate(df_all['Blend'].unique()):
    subset = df_all[df_all['Blend'] == blend]
    subset['Fuel1_share']*=100
    plt.plot(subset['Fuel1_share'], subset['LCOE'], label=blend,
             linestyle=styles[idx],ms=8)

plt.xlabel('Fuel 1 Energy Share')
plt.ylabel('LCOE (EUR / MWhₑ)')
plt.title('LCOE for binary fuel blends')
plt.legend(title='Fuel Blend [Fuel 1_Fuel 2]')
plt.tight_layout()
plt.show()




# Vol
plt.figure(figsize=(10, 6))
sns.set_style("whitegrid")

for idx, blend in enumerate(df_all['Blend'].unique()):
    subset = df_all[df_all['Blend'] == blend]
    subset['Fuel1_vol_share']*=100
    plt.plot(subset['Fuel1_vol_share'], subset['LCOE'], label=blend,
             linestyle=styles[idx],ms=8)

plt.xlabel('Fuel 1 Volumetric Share')
plt.ylabel('LCOE (EUR / MWhₑ)')
plt.title('LCOE for binary fuel blends')
plt.legend(title='Fuel Blend [Fuel 1_Fuel 2]',fontsize=15)
plt.yticks(range(100,118,2))
plt.tight_layout()
# plt.savefig('LCOE - Binary',dpi=300)










# Plot: Marginal Cost of Electricity vs. Fuel 1 Share
plt.figure(figsize=(10, 6))
sns.set_style("whitegrid")

for idx, blend in enumerate(df_all['Blend'].unique()):
    subset = df_all[df_all['Blend'] == blend]
    subset['Fuel1_share']*=100
    plt.plot(subset['Fuel1_share'], subset['Fuel_cost'], label=blend,
             linestyle=styles[idx],ms=8)

plt.xlabel('Fuel 1 Energy Share')
plt.ylabel('Marginal cost of electricity (EUR / MWhₑ)')
plt.title('Marginal cost of electricity for Binary Fuel Blends')
plt.legend(title='Fuel Blend [Fuel 1_Fuel 2]')
plt.tight_layout()
plt.show()





# Plot: Marginal Cost of Electricity vs. Fuel 1 Share
plt.figure(figsize=(10, 6))
sns.set_style("whitegrid")

for idx, blend in enumerate(df_all['Blend'].unique()):
    subset = df_all[df_all['Blend'] == blend]
    subset['Fuel1_vol_share']*=100
    plt.plot(subset['Fuel1_vol_share'], subset['Fuel_cost'], label=blend,
             linestyle=styles[idx],ms=8)

plt.xlabel('Fuel 1 Volumetric Share')
plt.ylabel('Marginal cost of electricity (EUR / MWhₑ)')
plt.title('Marginal cost of electricity for Binary Fuel Blends')
plt.legend(title='Fuel Blend [Fuel 1_Fuel 2]')
plt.tight_layout()
# plt.savefig('MC - Binary',dpi=300)




























fig, axs = plt.subplots(1,2,figsize=(22,6))
sns.set_style("whitegrid")


for idx, blend in enumerate(df_all['Blend'].unique()):
    subset = df_all[df_all['Blend'] == blend]
    subset['Fuel1_vol_share']*=100
    axs[0].plot(subset['Fuel1_vol_share'], subset['Fuel_cost'], label=blend,
             linestyle=styles[idx],ms=8,lw=4)

axs[0].set_title(label='Marginal cost of electricity',fontsize=22)
axs[0].set_ylabel('Eur/MWh',fontsize=18)
axs[0].set_xlabel('Fuel 1 Volumetric Share',fontsize=20)
axs[0].grid(True, which='both', linestyle='--', linewidth=0.7, color='gray')
axs[0].set_yticks(list(range(150,200,10)))
handles, labels = axs[0].get_legend_handles_labels()
axs[0].legend("")
axs[0].tick_params(axis='both', labelsize=18)


for idx, blend in enumerate(df_all['Blend'].unique()):
    subset = df_all[df_all['Blend'] == blend]
    subset['Fuel1_vol_share']*=100
    axs[1].plot(subset['Fuel1_vol_share'], subset['LCOE'], label=blend,
             linestyle=styles[idx],ms=8,lw=4)

axs[1].set_title(label='Levelized cost of electricity',fontsize=22)
axs[1].set_ylabel('Eur/MWh',fontsize=18)
axs[1].set_xlabel('Fuel 1 Volumetric Share',fontsize=20)
axs[1].grid(True, which='both', linestyle='--', linewidth=0.7, color='gray')
axs[1].legend("")
axs[1].set_yticks(list(range(100,118,2)))
axs[1].tick_params(axis='both', labelsize=18)


for h in handles:
    h.set_linewidth(4)
axs[1].legend(handles=handles, labels=labels, ncol=4,
              fontsize=22, bbox_to_anchor=[0.6, -0.13],
              title='Fuel Blend [Fuel 1_Fuel 2]', title_fontsize=24)
plt.savefig('Figures/Binary',dpi=300,bbox_inches='tight')








