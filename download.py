#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import codecs
import csv
import gzip
import pickle
import time
import zipfile
from multiprocessing import Manager, Pool, cpu_count
from os import makedirs
from os.path import exists
from typing import Dict, List, Union

import numpy as np
import requests
from bs4 import BeautifulSoup

# Kromě vestavěných knihoven (os, sys, re, requests …) byste si měli vystačit s: gzip, pickle, csv, zipfile, numpy, matplotlib, BeautifulSoup.
# Další knihovny je možné použít po schválení opravujícím (např ve fóru WIS).

class DataDownloader:
    """Attributes:
        headers         Nazvy hlavicek jednotlivych CSV souboru, tyto nazvy nemente!  
        header_types    Dictionary s numpy typy hlavicek
        regions         Dictionary s nazvy kraju : nazev csv souboru
    """

    headers = ["p1", "p36", "p37", "p2a", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a",
               "p13b", "p13c", "p14", "p15", "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p27", "p28",
               "p34", "p35", "p39", "p44", "p45a", "p47", "p48a", "p49", "p50a", "p50b", "p51", "p52", "p53", "p55a",
               "p57", "p58", "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "n", "o", "p", "q", "r", "s", "t", "p5a"]

    header_types = {
        #identifikační číslo            #druh pozemní komunikace    #číslo pozemní komunikace   #den, měsíc, rok
        "p1"           : np.uint64,     "p36"  : np.uint8,          "p37"  : np.uint32,         "p2a"  : np.unicode_,
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
        "p28"          : np.uint8,      "p34"  : np.uint8,          "p35"  : np.uint8,          "p39"  : np.uint8,
        #druh vozidla                   #výrobní značka             #výrobní rok                #charakteristika vozidla
        "p44"          : np.uint8,      "p45a" : np.uint16,         "p47"  : np.uint8,          "p48a" : np.uint8, 
        #smyk                           #vozidlo po nehodě          #únik hmot                  #způsob vyproštění osob z vozidla
        "p49"          : np.uint8,      "p50a" : np.uint8,          "p50b" : np.uint8,          "p51"  : np.uint8, 
        #směr jízdy,postavení vozidla   #škoda na vozidle           #kategorie řidiče           #stav řidiče
        "p52"          : np.uint8,      "p53"  : np.uint32,         "p55a" : np.uint8,          "p57"  : np.uint8,
        #vnější ovlivnění řidiče
        "p58"          : np.uint8,      "a"    : np.double,         "b"    : np.double,         "d"    : np.double,
        "e"            : np.double,     "f"    : np.double,         "g"    : np.double,         "h"    : np.unicode_,
        "i"            : np.unicode_,   "j"    : np.unicode_,       "k"    : np.unicode_,       "l"    : np.unicode_, 
        "n"            : np.uint32,     "o"    : np.unicode_,       "p"    : np.unicode_,       "q"    : np.unicode_,
                                                                                                #lokalita nehody
        "r"            : np.uint32,     "s"    : np.uint32,         "t"    : np.unicode_,        "p5a"  : np.uint8
    }

    regions = {
        "PHA": "00", "STC": "01", "JHC": "02", "PLK": "03",
        "ULK": "04", "HKK": "05", "JHM": "06", "MSK": "07",
        "OLK": "14", "ZLK": "15", "VYS": "16", "PAK": "17",
        "LBK": "18", "KVK": "19",
    }


    def __init__(self, url:str="https://ehw.fit.vutbr.cz/izv/", folder:str="data", cache_filename:str="data_{}.pkl.gz"):
        self.url = url
        self.folder = folder
        self.downloaded = False
        self.extracted_data = { region : None for region in self.regions.keys() }
        self.cache_file = f"{folder}/{cache_filename}"


    def download_data(self) -> None:
        # Parsování HTML stránky a načtení seznamu souborů ke stažení.
        page = requests.get(self.url).text
        soup = BeautifulSoup(page, 'html.parser')
        file_urls = [ self.url + node.get("onclick").replace("download('", "").replace("')", "")
            for node in soup.find_all("button")
            if node.get("onclick").endswith(".zip')") and node.get("onclick").startswith(f"download('{self.folder}/")
        ]
        # Cílová složka nemusí existovat, pokus o její vytvoření.
        try: makedirs(self.folder)
        except FileExistsError: pass

        # Seznam stažených souborů.
        manager = Manager()
        self.downloaded_zips : List[str] = manager.list()

        # Paralelní stažení všech sourobů.
        pool = Pool(cpu_count())
        pool.map(self._download_subroutine, file_urls)
        pool.close()
        pool.join()
        self.downloaded = True


    def _download_subroutine(self, file_url:str) -> None:
        """Podprogram pro stažení souboru spouštěný paralelně."""

        # Získání cesty souboru smazáním url.
        file_path = file_url.replace(self.url, "")
        self.downloaded_zips.append(file_path)

        # Nestahovat znovu, pokud soubor existuje.
        if exists(file_path):
            return

        # Proces stažení souboru.
        self._print_message(f"Downloading {file_url}...")
        with open(file_path, "wb") as file:
            with requests.get(file_url, stream=True) as data:
                for chunk in data:
                    file.write(chunk)
        self._print_message(f"Done downloading {file_url}...")


    def _create_empty_data_dict(self) -> Dict[str, np.ndarray]:
        """Vytvoření slovníku s hlavičkami a prázdnými numpy poli."""
        return { header : np.empty(shape=0, dtype=self.header_types[header]) for header in self.headers }


    def parse_region_data(self, region:str) -> Dict[str, np.ndarray]:
        if not self.downloaded:
            self.download_data()
        
        region_csv_name = self.regions[region] + ".csv"
        data = self._create_empty_data_dict()

        for zip_path in self.downloaded_zips:
            with zipfile.ZipFile(zip_path, "r") as zf:
                with zf.open(region_csv_name, "r") as csv_file: #V každém zip souboru, otevřít csv soubor daného kraje
                    reader = csv.reader(codecs.iterdecode(csv_file, "cp1250"), delimiter=';', quotechar='"')
                    #Načíst jednotlivé řádky souboru
                    for row in reader:
                        #Přeskočit řádky s prázdnými a nevalidními položkami
                        if any(self.header_types[header] is not np.unicode_ and row[i] in ("", "XX") for i, header in enumerate(self.headers)):
                            continue

                        for i, header in enumerate(self.headers):
                            #Úprava desetinné čárky na tečku
                            if self.header_types[header] is np.double:
                                row[i] = row[i].replace(',', '.')

                            data[header] = np.append(data[header], self.header_types[header](row[i]))

        data["region"] = np.full(data["p1"].size, region)
        return data


    def get_dict(self, regions:Union[None, List[str]]=None) -> Dict[str, np.ndarray]:
        if regions is None or len(regions) == 0:
            regions = list(self.regions.keys())

        data = self._create_empty_data_dict()
        data["region"] = np.empty(shape=0, dtype=np.unicode_)

        for region in regions:
            self._print_message(f"Parsing data for {region} region...")

            #Extrahovaná data pro daný kraj nejsou v paměti, načíst z cache.
            if self.extracted_data[region] is None:
                filename = self.cache_file.format(region)
                self.extracted_data[region] = self._load_cache(filename)

                #Cache neexistuje, načíst metodou parse_region_data a uložit cache.
                if self.extracted_data[region] is None:
                    self.extracted_data[region] = self.parse_region_data(region)
                    self._save_cache(filename, self.extracted_data[region])

            for header in self.extracted_data[region].keys():
                data[header] = np.concatenate((data[header], self.extracted_data[region][header]))

            self._print_message(f"Done parsing data for {region} region...")
        return data


    @staticmethod
    def _load_cache(filename:str) -> Union[Dict[str, np.ndarray], None]:
        """Načtení dat z cache souboru, pokud existuje, jinak None."""
        if not exists(filename):
            return None

        with gzip.open(filename, "rb") as file:
            return pickle.load(file)


    @staticmethod
    def _save_cache(filename:str, data:Dict[str, np.ndarray]) -> None:
        """Uložení dat do cache souboru."""
        with gzip.open(filename, "wb") as file:
            pickle.dump(data, file)


    @staticmethod
    def _print_message(message:str) -> None:
        """Výpis zprávy na standardní výstup, pokud je download.py spuštěn jako hlavní skript."""
        if __name__ in ("__main__", "__mp_main__"):
            print(message)


def main() -> None:
    start = time.time()
    downloader = DataDownloader()
    data = downloader.get_dict(regions=["JHC", "JHM", "VYS"])

    #Vypsat informace o zpracovaných krajích
    print("Data processed in {:.2f} seconds.".format(time.time() - start))
    print("Data contains {} rows.".format(data["region"].size))
    print("Data contains {} columns.".format(len(data)))
    print("Regions:", np.unique(data["region"]))


# TODO vypsat zakladni informace pri spusteni python3 download.py (ne pri importu modulu)
if __name__ == "__main__":
    main()
