#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#%%
from argparse import ArgumentParser
from os import makedirs
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors

from download import DataDownloader

# povolene jsou pouze zakladni knihovny (os, sys) a knihovny numpy, matplotlib a argparse
#%%
P24_LABELS = [
    "Žádná úprava",
    "Přerušovaná žlutá",
    "Semafor mimo provoz",
    "Dopravní značky",
    "Přenosné dopravní značky",
    "Nevyznačena",
]

#%%
def plot_stat(data_source:Dict[str, np.ndarray], fig_location:str=None, show_figure:bool=False) -> None:
    regions = np.unique(data_source["region"])
    p24_size = len(P24_LABELS)
    stats_abs = np.empty((p24_size, regions.size))
    stats_rel = np.empty_like(stats_abs)

    for i, region in enumerate(regions):
        indeces = np.argwhere(data_source["region"] == region).flatten()
        counts = np.bincount(data_source["p24"][indeces], minlength=p24_size)
        stats_abs[:, i] = counts
        stats_rel[:, i] = (counts / counts.sum()) * 100

    fig, axs = plt.subplots(2, 1, figsize=(6, 6))

    cmap = plt.get_cmap("viridis").copy()
    cmap.set_under("white")
    
    im1 = axs[0].imshow(stats_abs, cmap=cmap, norm=colors.LogNorm(vmin=1))
    im2 = axs[1].imshow(stats_rel, cmap=cmap, vmin=0.1, vmax=100)

    for ax in axs:
        ax.set_xticks(np.arange(regions.size))
        ax.set_yticks(np.arange(p24_size))
        ax.set_xticklabels(regions)
        ax.set_yticklabels(P24_LABELS)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    plt.colorbar(im1, shrink=0.5, ax=axs[0], label="Počet nehod")
    plt.colorbar(im2, shrink=0.5, ax=axs[1], label="Podíl nehod pro danou příčinu [%]")

    axs[0].set_title("Absoulutně")
    axs[1].set_title("Relativně vůči příčině")
    fig.tight_layout()
    
    if fig_location is not None:
        makedirs('/'.join(fig_location.split('/')[:-1]), exist_ok=True)
        plt.savefig(fig_location)

    if show_figure:
        plt.show()


#%%
def main() -> None:
    parser = ArgumentParser()
    parser.add_argument('--fig_location', type=str, default=None, help='Figure location')
    parser.add_argument('--show_figure', action="store_true", help='Show figure')
    args = parser.parse_args()
#%%
    data_source = DataDownloader().get_dict()
#%%
    plot_stat(data_source, args.fig_location, args.show_figure)
#%%

# TODO pri spusteni zpracovat argumenty
if __name__ == "__main__":
    main()
