#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import codecs
import csv
import time
import zipfile
from multiprocessing import Manager, Pool, cpu_count
from os import mkdir
from os.path import exists
from typing import Dict, List

import numpy as np
import requests
from bs4 import BeautifulSoup

# Kromě vestavěných knihoven (os, sys, re, requests …) byste si měli vystačit s: gzip, pickle, csv, zipfile, numpy, matplotlib, BeautifulSoup.
# Další knihovny je možné použít po schválení opravujícím (např ve fóru WIS).

class DataDownloader:
    """ TODO: dokumentacni retezce 

    Attributes:
        headers         Nazvy hlavicek jednotlivych CSV souboru, tyto nazvy nemente!  
        regions         Dictionary s nazvy kraju : nazev csv souboru
        header_types    Dictionary s typy hlavicek jednotlivych CSV souboru
    """

    headers = ["p1", "p36", "p37", "p2a", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a",
               "p13b", "p13c", "p14", "p15", "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p27", "p28",
               "p34", "p35", "p39", "p44", "p45a", "p47", "p48a", "p49", "p50a", "p50b", "p51", "p52", "p53", "p55a",
               "p57", "p58", "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "n", "o", "p", "q", "r", "s", "t", "p5a"]

    header_types = {
        #identifikační číslo            #druh pozemní komunikace    #číslo pozemní komunikace   #den, měsíc, rok
        "p1"           : np.uint64,     "p36"  : np.uint8,          "p37"  : np.float64,        "p2a"  : np.str0,
        #den v týdnu                    #čas                        #druh nehody                #druh srážky jedoucích vozidel
        "weekday(p2a)" : np.uint8,      "p2b"  : np.uint16,         "p6"   : np.uint8,          "p7"   : np.uint8,
        #druh pevné překážky            #charakter nehody           #zavinění nehody            #alkohol u viníka nehody přítomen
        "p8"           : np.uint8,      "p9"   : np.uint8,          "p10"  : np.uint8,          "p11"  : np.uint8, 
        #hlavní příčiny nehody          #usmrceno osob              #těžce zraněno osob         #lehce zraněno osob
        "p12"          : np.uint16,     "p13a" : np.uint8,          "p13b" : np.uint8,          "p13c" : np.uint8,
        #celková hmotná škoda           #druh povrchu vozovky       #stav povrchu vozovky       #stav komunikace
        "p14"          : np.uint32,     "p15"  : np.uint8,          "p16"  : np.uint8,          "p17"  : np.uint8,
        #povětrnostní podmínky          #viditelnost                #rozhledové poměry          #dělení komunikace 
        "p18"          : np.uint8,      "p19"  : np.uint8,          "p20"  : np.uint8,          "p21"  : np.uint8,
        #situování nehody               #řízení provozu             #místní úprava přednosti    #specifická místa a objekty v místě nehody
        "p22"          : np.uint8,      "p23"  : np.uint8,          "p24"  : np.uint8,          "p27"  : np.uint8,
        #směrové poměry                 #počet zúčastněných vozidel #místo dopravní nehody      #druh křižující komunikace
        "p28"          : np.uint8,      "p34"  : np.uint8,          "p35"  : np.uint8,          "p39"  : np.float64,
        #druh vozidla                   #výrobní značka             #výrobní rok                #charakteristika vozidla
        "p44"          : np.uint8,      "p45a" : np.uint16,         "p47"  : np.uint8,          "p48a" : np.uint8, 
        #smyk                           #vozidlo po nehodě          #únik hmot                  #způsob vyproštění osob z vozidla
        "p49"          : np.uint8,      "p50a" : np.uint8,          "p50b" : np.uint8,          "p51"  : np.uint8, 
        #směr jízdy,postavení vozidla   #škoda na vozidle           #kategorie řidiče           #stav řidiče
        "p52"          : np.uint8,      "p53"  : np.uint32,         "p55a" : np.uint8,          "p57"  : np.uint8,
        #vnější ovlivnění řidiče
        "p58"          : np.uint8,      "a"    : np.float64,        "b"    : np.float64,        "d"    : np.float64,
        "e"            : np.float64,    "f"    : np.float64,        "g"    : np.float64,        "h"    : np.str0,
        "i"            : np.str0,       "j"    : np.str0,           "k"    : np.str0,           "l"    : np.str0, 
        "n"            : np.uint32,     "o"    : np.str0,           "p"    : np.str0,           "q"    : np.str0,
                                                                                                #lokalita nehody
        "r"            : np.uint32,     "s"    : np.uint32,         "t"    : np.str0,           "p5a"  : np.uint8
    }
    #"a",b,d,e,f : np.float64

    regions = {
        "PHA": "00", "STC": "01", "JHC": "02", "PLK": "03",
        "ULK": "04", "HKK": "05", "JHM": "06", "MSK": "07",
        "OLK": "14", "ZLK": "15", "VYS": "16", "PAK": "17",
        "LBK": "18", "KVK": "19",
    }

    def __init__(self, url:str="https://ehw.fit.vutbr.cz/izv/", folder:str="data", cache_filename:str="data_{}.pkl.gz"):
        self.url = url
        self.folder = folder
        self.cache_filename = cache_filename


    def download_data(self):
        # Parsování HTML stránky a načtení seznamu souborů ke stažení.
        page = requests.get(self.url).text
        soup = BeautifulSoup(page, 'html.parser')
        file_urls = [ self.url + node.get("onclick").replace("download('", "").replace("')", "")
            for node in soup.find_all("button")
            if node.get("onclick").endswith(".zip')") and node.get("onclick").startswith(f"download('{self.folder}/")
        ]
        # Cílová složka nemusí existovat, pokus o její vytvoření.
        try: mkdir(self.folder)
        except FileExistsError: pass

        # Seznam stažených souborů.
        manager = Manager()
        self.downloaded_zips : List[str] = manager.list()

        # Paralelní stažení všech sourobů.
        pool = Pool(cpu_count())
        pool.map(self._download_file, file_urls)
        pool.close()
        pool.join()


    def _download_file(self, file_url:str):
        # Získání cesty souboru smazáním url.
        file_path = file_url.replace(self.url, "")
        self.downloaded_zips.append(file_path)

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


    def parse_region_data(self, region:str) -> Dict[str, np.ndarray]:
        self.download_data()
        region_csv_name = self.regions[region] + ".csv"
        data = { header : [] for header in self.headers }

        for zip_path in self.downloaded_zips:
            with zipfile.ZipFile(zip_path, "r") as zf:
                with zf.open(region_csv_name, "r") as csv_file: #V každém zip souboru, otevřít csv soubor daného kraje
                    reader = csv.reader(codecs.iterdecode(csv_file, "cp1250"), delimiter=';', quotechar='"')
                    #Načíst jednotlivé řádky souboru
                    for row in reader:
                        row = dict(zip(self.headers, row))
                        skip_row = False
                        #Přeskočit nevalidní řádky
                        for header in self.headers:
                            if row[header] in ["", "XX"]:
                                #Pro float přiřadit NaN
                                if self.header_types[header] is np.float64:
                                    row[header] = np.nan
                                #Pro ostatní typy přeskočit
                                elif self.header_types[header] is not np.str0:
                                    skip_row = True
                                    break
                        if skip_row:
                            continue
                        #Přidat řádek do data
                        for header in self.headers:
                            #Úprava dat pro float (',' na '.')
                            if self.header_types[header] is np.float64 and row[header] is not np.nan:
                                row[header] = row[header].replace(",", ".")
                            data[header].append(row[header])
        #Konverze seznamů s daty na numpy array
        for header in self.headers:
            data[header] = np.array(data[header], dtype=self.header_types[header])

            print(header, end=":\t")
            print(data[header].shape, end=",\t")
            print(data[header].dtype)
        return data


    def get_dict(self, regions=None):
        pass


def main():
    start = time.time()
    downloader = DataDownloader()
    jhm_dict = downloader.parse_region_data("JHM")
    print("--- %s seconds ---" % (time.time() - start))

# TODO vypsat zakladni informace pri spusteni python3 download.py (ne pri importu modulu)
if __name__ == "__main__":
    main()
