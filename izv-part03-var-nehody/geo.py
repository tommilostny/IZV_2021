#!/usr/bin/python3.8
# coding=utf-8
# %%
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily
import sklearn.cluster
import numpy as np
# muzete pridat vlastni knihovny

# %%
def make_geo(df: pd.DataFrame) -> gpd.GeoDataFrame:
    """ Konvertovani dataframe do geopandas.GeoDataFrame se spravnym kodovanim. """
    df = df.dropna(subset=['d', 'e']).copy()

    return gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(x=df["d"], y=df["e"]), crs="epsg:3857")

# %%
def plot_geo(gdf: gpd.GeoDataFrame, fig_location: str = None,
             show_figure: bool = False):
    """ Vykresleni grafu s sesti podgrafy podle lokality nehody 
     (dalnice vs prvni trida) pro roky 2018-2020 """
    pass

# %%
def plot_cluster(gdf: gpd.GeoDataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """ Vykresleni grafu s lokalitou vsech nehod v kraji shlukovanych do clusteru """
    pass

# %%
if __name__ == "__main__":
# %%
    # zde muzete delat libovolne modifikace
    df = pd.read_pickle("accidents.pkl.gz")
# %%
    gdf = make_geo(df)
# %%
    plot_geo(gdf, "geo1.png", True)
# %%
    plot_cluster(gdf, "geo2.png", True)
