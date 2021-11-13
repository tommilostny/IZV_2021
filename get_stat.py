#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from os import makedirs
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np

from download import DataDownloader

# povolene jsou pouze zakladni knihovny (os, sys) a knihovny numpy, matplotlib a argparse

def plot_stat(data_source:Dict[str, np.ndarray], fig_location:str=None, show_figure:bool=False) -> None:
    if fig_location is not None:
        makedirs('/'.join(fig_location.split('/')[:-1]), exist_ok=True)
        #plt.savefig(fig_location)

    if show_figure:
        #plt.show()
        print("SHOW")


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument('--fig_location', type=str, default=None, help='Figure location')
    parser.add_argument('--show_figure', action="store_true", help='Show figure')
    args = parser.parse_args()

    plot_stat(DataDownloader().get_dict(), args.fig_location, args.show_figure)


# TODO pri spusteni zpracovat argumenty
if __name__ == "__main__":
    main()
