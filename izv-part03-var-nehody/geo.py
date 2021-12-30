#!/usr/bin/python3.8
# coding=utf-8
# %%
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import sklearn.cluster
import numpy as np
# muzete pridat vlastni knihovny

SELECTED_REGION = "VYS"

# %%
def make_geo(df: pd.DataFrame) -> gpd.GeoDataFrame:
    """ Konvertovani dataframe do geopandas.GeoDataFrame se spravnym kodovanim. """

    # Smazání řádků, které neobsahují souřadnice
    df = df.dropna(subset=['d', 'e']).copy()

    # Konverze na geopandas.GeoDataFrame s CRS pro GPS (EPSG:3857)
    return gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(x=df["d"], y=df["e"]), crs="epsg:5514")

# %%
def plot_geo(gdf: gpd.GeoDataFrame, fig_location: str = None,
             show_figure: bool = False):
    """ Vykresleni grafu s sesti podgrafy podle lokality nehody 
     (dalnice vs prvni trida) pro roky 2018-2020 """
    
    # Výběr regionu do nového dataframe
    gdf = gdf[["region", "geometry", "p2a", "p36"]][gdf["region"] == SELECTED_REGION].copy()

    # Získání data a filtrování roků 2018-2020
    gdf["year"] = pd.to_datetime(gdf["p2a"], format="%Y-%m-%d").dt.year
    gdf = gdf[gdf["year"].isin([2018, 2019, 2020])]

    # Filtrování typů silnic (0 => dálnice, 1 => silnice 1. třídy)
    gdf = gdf[gdf["p36"].isin([0, 1])]

    # Převod souřadnic na GPS pro zobrazení
    gdf = gdf.to_crs("epsg:3857")
    
    # Vytvoření mapy
    fig, axes = plt.subplots(3, 2, figsize=(15, 18))
    fig.set_facecolor("#fefefe")

    # Podgrafy pro všechny roky 2018-2020 (řádky), druhy silnic p36 (sloupce)
    for row, (year, group) in enumerate(gdf.groupby("year")):
        for col, (road_type, subgroup) in enumerate(group.groupby("p36")):
            ax = axes[row, col]

            ax.set_title(f"{SELECTED_REGION} kraj: {'dálnice' if road_type == 0 else 'silnice 1. třídy'} ({year})")
            ax.set_aspect('equal')
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)

            ax.set_xlim(gdf["geometry"].total_bounds[0], gdf["geometry"].total_bounds[2])
            ax.set_ylim(gdf["geometry"].total_bounds[1], gdf["geometry"].total_bounds[3])

            subgroup.plot(ax=ax, color='red', markersize=1)
            ctx.add_basemap(ax, crs=gdf.crs.to_string(), source=ctx.providers.Stamen.TonerLite)

    # Zobrazení a uložení grafu
    fig.tight_layout()
    if show_figure:
        fig.show()
    if fig_location:
        fig.savefig(fig_location, dpi=500)

# %%
def plot_cluster(gdf: gpd.GeoDataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """ Vykresleni grafu s lokalitou vsech nehod v kraji shlukovanych do clusteru """
    pass

# %%
if __name__ == "__main__":
    # zde muzete delat libovolne modifikace
# %%
    df = pd.read_pickle("accidents.pkl.gz")
# %%
    gdf = make_geo(df)
# %%
    plot_geo(gdf, "geo1.png", True)
# %%
    plot_cluster(gdf, "geo2.png", True)
