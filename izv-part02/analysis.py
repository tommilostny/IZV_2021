#!/usr/bin/env python3.9
# coding=utf-8
# %%
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
        if col not in ["region", "p21", "date"]:
            df[col] = df[col].astype("category")      
    if verbose:
        print(f"new_size={df.memory_usage(deep=True, index=True).sum() / 1_048_576:.1f} MB")
    
    return df

# %%
# Ukol 2: počty nehod v jednotlivých regionech podle druhu silnic

ROADTYPE_LABELS = {
    1: "Dvoupruhová komunikace",
    2: "Třípruhová komunikace",
    3: "Čtyřpruhová komunikace",
    4: "Čtyřpruhová komunikace",
    5: "Vícepruhová komunikace",
    6: "Rychlostní komunikace",
    0: "Jiná komunikace",
}

def plot_roadtype(df: pd.DataFrame, fig_location: str = None,
                  show_figure: bool = False):
    # Copy selected 4 regions and p21 columns from df into new df_roadtype 
    df_roadtype = df[["region", "p21"]][df["region"].isin(["MSK", "JHM", "KVK", "JHC"])].copy()

    # Add roadtype_label column to match column p21
    df_roadtype["roadtype_label"] = df_roadtype["p21"].map(ROADTYPE_LABELS)

    # Create 3*2 subplots
    fig, axes = plt.subplots(3, 2, figsize=(10, 10))
    fig.suptitle("Druhy silnic", fontsize=18)
    fig.set_facecolor("#fefefe")
    axes = axes.flatten()

    # For each roadtype_label, plot regions using seaborn
    for index, (roadtype_label, group) in enumerate(df_roadtype.groupby("roadtype_label")):        
        ax = axes[index]
        sns.countplot(x="region", data=group, ax=ax, hue="region")

        ax.set_title(roadtype_label)
        ax.set_ylabel("Počet nehod")
        ax.set_xlabel("Kraj")
        ax.legend().set_visible(False)
        ax.set_facecolor("#f0f0f0")

    fig.tight_layout()
    if show_figure:
        fig.show()
    if fig_location:
        fig.savefig(fig_location)

# %%
# Ukol3: zavinění zvěří
def plot_animals(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    pass

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
