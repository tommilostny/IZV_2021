#!/usr/bin/env python3.9
# coding=utf-8
# %%
from typing import List
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os

# muzete pridat libovolnou zakladni knihovnu ci knihovnu predstavenou na prednaskach
# dalsi knihovny pak na dotaz

""" Ukol 1:
načíst soubor nehod, který byl vytvořen z vašich dat. Neznámé integerové hodnoty byly mapovány na -1.

Úkoly:
- vytvořte sloupec date, který bude ve formátu data (berte v potaz pouze datum, tj sloupec p2a)
- vhodné sloupce zmenšete pomocí kategorických datových typů. Měli byste se dostat po 0.5 GB. Neměňte však na kategorický typ region (špatně by se vám pracovalo s figure-level funkcemi)
- implementujte funkci, která vypíše kompletní (hlubkou) velikost všech sloupců v DataFrame v paměti:
orig_size=X MB
new_size=X MB

Poznámka: zobrazujte na 1 desetinné místo (.1f) a počítejte, že 1 MB = 1e6 B. 
"""

# %%
def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    df = pd.read_pickle(filename)

    # Add date column
    df["date"] = pd.to_datetime(df["p2a"], format="%Y-%m-%d")
    if verbose:
        print(f"orig_size={df.memory_usage(deep=True, index=True).sum() / 1_048_576:.1f} MB")
    
    # Convert each col in df to categorical
    for col in df.columns:
        if col not in ["region", "p21", "date", "p10"]:
            df[col] = df[col].astype("category")      
    if verbose:
        print(f"new_size={df.memory_usage(deep=True, index=True).sum() / 1_048_576:.1f} MB")
    
    return df

# %%
SELECTED_REGIONS = ("MSK", "JHM", "KVK", "JHC")

def copy_selected_regions(df: pd.DataFrame, columns: List[str]):
    # Return a copy columns of df from 4 selected regions 
    return df[columns][df["region"].isin(SELECTED_REGIONS)].copy()

# %%
# Ukol 2: počty nehod v jednotlivých regionech podle druhu silnic

def map_roadtype(p21_value: int) -> str:
    if p21_value == 1:
        return "Dvoupruhová komunikace"
    elif p21_value == 2:
        return "Třípruhová komunikace"
    elif p21_value == 3 or p21_value == 4:
        return "Čtyřpruhová komunikace"
    elif p21_value == 5:\
        return "Vícepruhová komunikace"
    elif p21_value == 6:
        return "Rychlostní komunikace"
    else:
        return "Jiná komunikace"

def plot_roadtype(df: pd.DataFrame, fig_location: str = None,
                  show_figure: bool = False):
    # Create a copy of df with only selected columns
    df_roadtype = copy_selected_regions(df, columns=["region", "p21"])

    # Modify p21 column to map labels
    df_roadtype["p21"] = df_roadtype["p21"].map(map_roadtype)

    # Create subplots for 6 road types
    fig, axes = plt.subplots(3, 2, figsize=(10, 10))
    fig.suptitle("Druhy silnic", fontsize=18)
    fig.set_facecolor("#fefefe")
    axes = axes.flatten()

    # For each road type, plot count of accidents in regions using seaborn
    for index, (road_type, group) in enumerate(df_roadtype.groupby("p21")):        
        ax = axes[index]
        sns.countplot(x="region", data=group, ax=ax, hue="region")

        ax.set_title(road_type)
        ax.set_ylabel("Počet nehod")
        ax.set_xlabel("Kraj")
        ax.legend().set_visible(False)
        ax.set_facecolor("#f0f0f0")

    # Display and save figure
    fig.tight_layout()
    if show_figure:
        fig.show()
    if fig_location:
        fig.savefig(fig_location)


# %%
# Ukol3: zavinění zvěří

def map_animal(p10_value: int) -> str:
    if p10_value == 1 or p10_value == 2:
        return "řidičem"
    elif p10_value == 4:
        return "zvěří"
    else:
        return "jiné"

def plot_animals(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    # Create a copy of df with only selected columns
    df_animals = copy_selected_regions(df, columns=["region", "date", "p10"])

    # Remove rows with date year == 2021
    df_animals = df_animals[df_animals["date"].dt.year != 2021]

    # Modify p10 column to map labels and date to months
    df_animals["p10"] = df_animals["p10"].map(map_animal)
    df_animals["date"] = df_animals["date"].dt.month

    # Sort by p10
    df_animals.sort_values(by=["p10", "region"], inplace=True, ascending=False)

    # Create subplots for 4 regions
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.set_facecolor("#fefefe")
    axes = axes.flatten()

    # For each region, plot animal type in accident by month using seaborn
    for index, (region, group) in enumerate(df_animals.groupby("region")):
        ax = axes[index]
        sns.countplot(x="date", data=group, ax=ax, hue="p10")

        ax.set_title(f"Kraj: {region}")
        ax.set_ylabel("Počet nehod")
        ax.set_xlabel("Měsíc")
        ax.legend().set_visible(False)

    # Display and save figure
    axes[0].legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0)
    fig.tight_layout()
    if show_figure:
        fig.show()
    if fig_location:
        fig.savefig(fig_location)



# %%
# Ukol 4: Povětrnostní podmínky
def plot_conditions(df: pd.DataFrame, fig_location: str = None,
                    show_figure: bool = False):
    pass

# %%
if __name__ == "__main__":
    # zde je ukazka pouziti, tuto cast muzete modifikovat podle libosti
    # skript nebude pri testovani pousten primo, ale budou volany konkreni ¨
    # funkce.
# %%
    df = get_dataframe("accidents.pkl.gz", verbose=True) # tento soubor si stahnete sami, při testování pro hodnocení bude existovat
# %%
    plot_roadtype(df, fig_location="01_roadtype.png", show_figure=True)
# %%
    plot_animals(df, "02_animals.png", True)
# %%
    plot_conditions(df, "03_conditions.png", True)
