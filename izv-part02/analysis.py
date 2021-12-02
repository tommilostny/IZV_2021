#!/usr/bin/env python3.9
# coding=utf-8
# %%
from typing import List
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns

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
        print(f"orig_size={df.memory_usage(deep=True).sum() / 1e6:.1f} MB")

    # Convert each col in df to categorical
    for col in df.columns:
        if col not in ["region", "date"]:
            df[col] = df[col].astype("category")
    if verbose:
        print(f"new_size={df.memory_usage(deep=True).sum() / 1e6:.1f} MB")

    return df

# %%


def _selected_regions(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Return a copy of df from 4 selected regions witg specified columns."""
    return df[columns][df["region"].isin(["MSK", "JHM", "VYS", "JHC"])].copy()

# %%
# Ukol 2: počty nehod v jednotlivých regionech podle druhu silnic


def _map_roadtype(p21_value: int) -> str:
    if p21_value == 1:
        return "Dvoupruhová komunikace"
    elif p21_value == 2:
        return "Třípruhová komunikace"
    elif p21_value == 3 or p21_value == 4:
        return "Čtyřpruhová komunikace"
    elif p21_value == 5:
        return "Vícepruhová komunikace"
    elif p21_value == 6:
        return "Rychlostní komunikace"
    else:
        return "Jiná komunikace"


def plot_roadtype(df: pd.DataFrame, fig_location: str = None,
                  show_figure: bool = False):
    # Create a copy of df with only selected columns
    df_roadtype = _selected_regions(df, columns=["region", "p21"])

    # Modify p21 column to map labels
    df_roadtype["p21"] = df_roadtype["p21"].map(_map_roadtype)

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


def _map_animal(p10_value: int) -> str:
    if p10_value == 1 or p10_value == 2:
        return "řidičem"
    elif p10_value == 4:
        return "zvěří"
    else:
        return "jiné"


def plot_animals(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    # Create a copy of df with only selected columns
    df_animals = _selected_regions(df, columns=["region", "date", "p10"])

    # Remove rows with date year == 2021
    df_animals = df_animals[df_animals["date"].dt.year != 2021]

    # Modify p10 column to map labels and date to months
    df_animals["p10"] = df_animals["p10"].map(_map_animal)
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
        ax.set_facecolor("#f0f0f0")

    # Display and save figure
    axes[0].legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0)
    fig.tight_layout()
    if show_figure:
        fig.show()
    if fig_location:
        fig.savefig(fig_location)

# %%
# Ukol 4: Povětrnostní podmínky


def _map_condition(p18_value: int) -> str:
    if p18_value == 1:
        return "neztižené"
    elif p18_value == 2:
        return "mlha"
    elif p18_value == 3:
        return "na počátku deště"
    elif p18_value == 4:
        return "déšť"
    elif p18_value == 5:
        return "sněžení"
    elif p18_value == 6:
        return "náledí"
    elif p18_value == 7:
        return "nárazový vítr"
    else:
        return "jiné"


def plot_conditions(df: pd.DataFrame, fig_location: str = None,
                    show_figure: bool = False):
    # Create a copy of df with only selected columns
    df_conditions = _selected_regions(df, columns=["region", "date", "p18"])

    # Reduce dataset to contain dates between 1.1.2016 and 1.1.2020
    df_conditions = df_conditions[(df_conditions["date"] >= "2016-01-01") &
                                  (df_conditions["date"] < "2020-01-01")]

    # Modify p18 column to map labels
    df_conditions["p18"] = df_conditions["p18"].map(_map_condition)

    # For each region, plot count of accidents by p18 using seaborn lineplot
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.set_facecolor("#fefefe")
    axes = axes.flatten()

    for index, (region, group) in enumerate(df_conditions.groupby("region")):
        group = group.pivot_table(index="date", columns="p18",
                                  values="region", aggfunc="count")
        # Remove column where p18 == 0
        group = group.drop(columns="jiné", axis=1)

        # Reduce date to month level
        group = group.resample("M").sum()

        # Plot group to lineplot
        ax = axes[index]
        group.plot(ax=ax, kind="line", legend=False, title=f"Kraj: {region}",
                   ylabel="Počet nehod", xlabel="")
        ax.set_facecolor("#f0f0f0")

        # Set x ticks to years
        ax.xaxis.set_ticks(group.index)
        ax.xaxis.set_ticklabels(group.index.strftime('%Y'))
        last = None
        for label in ax.xaxis.get_ticklabels():
            if last == label.get_text():
                label.set_visible(False)
            last = label.get_text()

    # Display and save figure
    axes[0].legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0)
    fig.tight_layout()
    if show_figure:
        fig.show()
    if fig_location:
        fig.savefig(fig_location)

# %%
if __name__ == "__main__":
    # zde je ukazka pouziti, tuto cast muzete modifikovat podle libosti
    # skript nebude pri testovani pousten primo, ale budou volany konkreni ¨
    # funkce.
    # %%
    df = get_dataframe("accidents.pkl.gz", verbose=True)
    # %%
    plot_roadtype(df, fig_location="01_roadtype.png", show_figure=True)
    # %%
    plot_animals(df, "02_animals.png", True)
    # %%
    plot_conditions(df, "03_conditions.png", True)
    # %%
