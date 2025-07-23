# -*- coding: utf-8 -*-
"""
@author: Anas Abuzayed © 2025
https://github.com/AnasAbuzayed/H2_CCGT

Description:
This script reproduces figure 5 All data used are cited in the main paper. 

"""


dpi=300
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ternary
from matplotlib.colors import LogNorm
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
retrofit_pct = 0.167702659 # Retrofit cost (constant here)





# Fuel costs (EUR/MWh_fuel)
H2_fuel_cost = 49.48 + 9.58 + 24.26 + 22.72 + 8.47 # Production + Liquefaction + shipping+distribution+regasification
NH3_fuel_cost = 49.48 + 34 + 9.08 + 3.44  # Production + Synthesis + shipping + distribution
NH3_cracking_fuel_cost = NH3_fuel_cost*1.2
CH4_fuel_cost = 97.19 + 4.71 # Production + Distribution


# Storage CAPEX (EUR/MWh_fuel)
H2_capex = 1091.02 
NH3_capex = 157.64
CH4_capex = 182.07

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
    initial = reserve * share * CAPEX * (1 + fcr_s) 
    money = sum((FOM_storage * initial) / ((1 + WACC) ** y) for y in range(1, storage_lifetime + 1))
    energy = sum(E / ((1 + WACC) ** y) for y in range(1, storage_lifetime + 1))
    return (initial + money) / energy * 1000

# Fuels and properties
fuels = {
    "H2": {"cost": H2_fuel_cost, "capex": H2_capex, "LHV":10.8},
    "NH3": {"cost": NH3_fuel_cost, "capex": NH3_capex, "LHV":12.7 },
    "NH3c": {"cost": NH3_cracking_fuel_cost, "capex": NH3_capex, "LHV":10.8},
    "CH4": {"cost": CH4_fuel_cost, "capex": CH4_capex, "LHV":35},
}


# Blending triplets
triplets = [("H2", "NH3", "CH4"), ("NH3", "NH3c", "CH4"),("H2", "NH3c", "CH4")]
share_grid = np.linspace(0, 1, 501)

results_tri = []

for f1, f2, f3 in triplets:
    for X1 in share_grid:
        for X2 in share_grid:
            if X1 + X2 > 1:
                continue
            
            X3 = 1 - X1 - X2         

            fuel_cost = X1 * fuels[f1]["cost"] + X2 * fuels[f2]["cost"] + X3 * fuels[f3]["cost"]
            lcos1 = lcos(reserve, X1, fuels[f1]["capex"])
            lcos2 = lcos(reserve, X2, fuels[f2]["capex"])
            lcos3 = lcos(reserve, X3, fuels[f3]["capex"])
            
            if 'NH3' in [f1,f2,f3]:
                retrofit_pct = 0.167702659 # Retrofit cost (constant here)
            else:
                retrofit_pct = 0.134098756 # Retrofit cost (constant here)

            firing_base = (capacity * capex * (1 + fcr_p) * (1 + retrofit_pct) + money) / energy * 1000

            LCOE =  lcos1 + lcos2 + lcos3 +  firing_base

            results_tri.append({
                "Blend": f"{f1}_{f2}_{f3}",
                "PCT": f"{retrofit_pct}",
                f"{f1}_share": X1,
                f"{f2}_share": X2,
                f"{f3}_share": X3,
                "LCOE": LCOE,
                "MCOE": fuel_cost/efficiency,
                "LCOE & MC": fuel_cost/efficiency + LCOE,
                "LCOS": lcos1 + lcos2 + lcos3 
                
            })

df_tri = pd.DataFrame(results_tri)

df_tri.replace(np.nan,0,inplace=True)


def draw_guides(point, color='r', linewidth=1, linestyle='--'):
    t, l, r = point
    # Guide to bottom axis (constant top component)
    tax.line((0, l, scale - l), point, linewidth=linewidth, linestyle=linestyle, color=color, zorder=1)
    # Guide to left axis (constant right component)
    tax.line((t, 0, scale - t), point, linewidth=linewidth, linestyle=linestyle, color=color, zorder=1)
    # Guide to right axis (constant left component)
    tax.line((t, scale - t, 0), point, linewidth=linewidth, linestyle=linestyle, color=color, zorder=1)



scale = 100


for blend in df_tri.Blend.unique():
    print(blend)
    for arg in ['LCOE','MCOE','LCOE & MC']:
        print(arg)
        
        df=df_tri.loc[df_tri.Blend==blend].copy()
        
        bottom, left, right = blend.split('_')
        for x in blend.split('_'):
            df[f'{x}_vol'] = (df_tri[f'{x}_share'] * fuels[x]['LHV']) /\
                (df_tri[f'{bottom}_share'] * fuels[bottom]['LHV'] +
                 df_tri[f'{left}_share'] * fuels[left]['LHV'] +
                 df_tri[f'{right}_share'] * fuels[right]['LHV'] )
        
        example_points = {
            "1": (60,30,10),
            "2": (70,0,30),
            "3": (0,60,40),
            "4": (100,0,0),
            "5": (10,20,70),
        }

        
        ternary_data = []
        for _, row in df.iterrows():
            point = (
                row[f"{bottom}_vol"] * scale,
                row[f"{left}_vol"] * scale,
                row[f"{right}_vol"] * scale,
            )
            ternary_data.append((point, np.sum(row[arg])))
        
        # Normalize
        values = [v for _, v in ternary_data]
        
        norm = LogNorm(vmin=max(min(values), 1), vmax=max(values))
        norm = plt.Normalize(min(values), max(values))

        # Initialize plot
        fig, ax = plt.subplots(figsize=(6, 5))
        tax = ternary.TernaryAxesSubplot(ax=ax, scale=scale)

        tax.get_axes().set_frame_on(False)
        fig.patch.set_facecolor('white')
        tax.get_axes().set_facecolor('white')

        tax.set_title(f"{arg} for {blend} Blend", fontsize=14,pad=20)
        tax.boundary()
        tax.gridlines(multiple=10, color="snow", linewidth=1)
        
        
        tax.bottom_axis_label(f"{bottom} [%]", fontsize=14, fontweight='bold', offset=0.18)
        tax.left_axis_label(f"{left} [%]", fontsize=14, fontweight='bold', offset=0.18)
        tax.right_axis_label(f"{right} [%]", fontsize=14, fontweight='bold', offset=0.18)

        cmap = plt.cm.viridis
        for (point, lcoe) in ternary_data:
            color = cmap(norm(lcoe))
            tax.scatter([point], color=color, s=2,alpha=0.7)
        
        # Colorbar
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=tax.get_axes(), pad=0.1)
        cbar.set_label(f"{arg} (EUR/MWh)", fontsize=12)
        if arg == 'MCOE':
            for label, coords in example_points.items():
                tax.scatter([coords], color='k', s=180, zorder=2,alpha=1)
                tax.annotate(
                    text=label,
                    position=coords,
                    fontsize=13,
                    color='gold',              
                    horizontalalignment='center',
                    verticalalignment='center'  # Center text inside the point
                )
            # for coords in example_points.values():
            #     draw_guides(coords)

        tax.ticks(axis='lbr', multiple=20,linewidth=1, offset=0.04, tick_formats="%d")

        tax.clear_matplotlib_ticks()
        tax._redraw_labels()
        plt.savefig(f'Figures/Ternary/{blend} - {arg}',dpi=dpi)
        plt.close(fig)
        plt.show()






# # plt.hist(lcoe_values, bins=50)
# # plt.title("LCOE Value Distribution")
# # plt.xlabel("LCOE (EUR/MWhₑ)")
# # plt.ylabel("Frequency")
# # plt.grid(True)
# # plt.show()








# # import matplotlib.pyplot as plt
# # from mpl_toolkits.mplot3d import Axes3D

# # # Prepare data
# # x = df_tri_hydrogen["H2_vol"]
# # y = df_tri_hydrogen["NH3_vol"]
# # z = df_tri_hydrogen["CH4_vol"]
# # c = df_tri_hydrogen["LCOE"]

# # # 3D scatter plot
# # fig = plt.figure(figsize=(10, 8))
# # ax = fig.add_subplot(111, projection='3d')
# # sc = ax.scatter(x, y, z, c=c, cmap='viridis', marker='o')

# # # Axis labels
# # ax.set_xlabel("H2 Share")
# # ax.set_ylabel("NH3 Share")
# # ax.set_zlabel("CH4 Share")
# # ax.set_title("LCOE vs. H2-NH3-CH4 Fuel Shares")

# # # Color bar
# # cb = fig.colorbar(sc, ax=ax, shrink=0.6)
# # cb.set_label("LCOE (EUR/MWhₑ)")

# # plt.tight_layout()
# # plt.show()










