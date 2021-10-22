#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import zipfile
from multiprocessing import Pool, cpu_count
from os import mkdir
from os.path import exists

import numpy as np
import requests
from bs4 import BeautifulSoup

# Kromě vestavěných knihoven (os, sys, re, requests …) byste si měli vystačit s: gzip, pickle, csv, zipfile, numpy, matplotlib, BeautifulSoup.
# Další knihovny je možné použít po schválení opravujícím (např ve fóru WIS).

class DataDownloader:
    """ TODO: dokumentacni retezce 

    Attributes:
        headers    Nazvy hlavicek jednotlivych CSV souboru, tyto nazvy nemente!  
        regions     Dictionary s nazvy kraju : nazev csv souboru
    """

    headers = ["p1", "p36", "p37", "p2a", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a",
               "p13b", "p13c", "p14", "p15", "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p27", "p28",
               "p34", "p35", "p39", "p44", "p45a", "p47", "p48a", "p49", "p50a", "p50b", "p51", "p52", "p53", "p55a",
               "p57", "p58", "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "n", "o", "p", "q", "r", "s", "t", "p5a"]

    regions = {
        "PHA": "00",
        "STC": "01",
        "JHC": "02",
        "PLK": "03",
        "ULK": "04",
        "HKK": "05",
        "JHM": "06",
        "MSK": "07",
        "OLK": "14",
        "ZLK": "15",
        "VYS": "16",
        "PAK": "17",
        "LBK": "18",
        "KVK": "19",
    }

    def __init__(self, url:str="https://ehw.fit.vutbr.cz/izv/", folder:str="data", cache_filename:str="data_{}.pkl.gz"):
        self.url = url
        self.folder = folder
        self.cache_filename = cache_filename


    def download_data(self):
        # Parsování HTML stránky a načtení seznamu souborů ke stažení.
        page = requests.get(self.url).text
        soup = BeautifulSoup(page, 'html.parser')
        files = [ self.url + node.get("onclick").replace("download('", "").replace("')", "")
            for node in soup.find_all("button")
            if node.get("onclick").endswith(".zip')") and node.get("onclick").startswith(f"download('{self.folder}/")
        ]
        # Cílová složka nemusí existovat, pokus o její vytvoření.
        try: mkdir(self.folder)
        except FileExistsError: pass

        # Paralelní stažení všech sourobů.
        pool = Pool(cpu_count())
        pool.map(self._download_file, files)
        pool.close()
        pool.join()


    def _download_file(self, file_url:str):
        # Získání cesty souboru smazáním url.
        file_path = file_url.replace(self.url, "")

        # Nestahovat znovu, pokud soubor existuje.
        if exists(file_path):
            return

        # Proces stažení souboru.
        print(f"Downloading {file_url}...")
        with open(file_path, "wb") as file:
            with requests.get(file_url, stream=True) as data:
                for chunk in data:
                    file.write(chunk)
        print(f"Done downloading {file_url}...")


    def parse_region_data(self, region):
        pass


    def get_dict(self, regions=None):
        pass


# TODO vypsat zakladni informace pri spusteni python3 download.py (ne pri importu modulu)
if __name__ == "__main__":
    start = time.time()

    downloader = DataDownloader()
    downloader.download_data()

    print("--- %s seconds ---" % (time.time() - start))
