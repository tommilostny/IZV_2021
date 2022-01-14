#!/usr/bin/python3.8
# coding=utf-8
# %%
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
# %%
# Automobilové výrobní značky (p45a)
CAR_BRANDS = {
    1: "ALFA-ROMEO",
    2: "AUDI",
    3: "AVIA",
    4: "BMW",
    5: "CHEVROLET",
    6: "CHRYSLER",
    7: "CITROEN",
    8: "DACIA",
    9: "DAEWOO",
    10: "DAF",
    11: "DODGE",
    12: "FIAT ",
    13: "FORD",
    14: "GAZ, VOLHA",
    15: "FERRARI",
    16: "HONDA",
    17: "HYUNDAI",
    18: "IFA",
    19: "IVECO",
    20: "JAGUAR",
    21: "JEEP",
    22: "LANCIA",
    23: "LAND ROVER",
    24: "LIAZ",
    25: "MAZDA",
    26: "MERCEDES",
    27: "MITSUBISHI",
    28: "MOSKVIČ",
    29: "NISSAN",
    30: "OLTCIT",
    31: "OPEL",
    32: "PEUGEOT",
    33: "PORSCHE",
    34: "PRAGA",
    35: "RENAULT",
    36: "ROVER",
    37: "SAAB",
    38: "SEAT",
    39: "ŠKODA",
    40: "SCANIA",
    41: "SUBARU",
    42: "SUZUKI",
    43: "TATRA",
    44: "TOYOTA",
    45: "TRABANT",
    46: "VAZ",
    47: "VOLKSWAGEN",
    48: "VOLVO",
    49: "WARTBURG",
    50: "ZASTAVA",
    51: "AGM",
    52: "ARO",
    53: "AUSTIN",
    54: "BARKAS",
    55: "DAIHATSU",
    56: "DATSUN",
    57: "DESTACAR",
    58: "ISUZU",
    59: "KAROSA",
    60: "KIA",
    61: "LUBLIN",
    62: "MAN",
    63: "MASERATI",
    64: "MULTICAR",
    65: "PONTIAC",
    66: "ROSS",
    67: "SIMCA",
    68: "SSANGYONG",
    69: "TALBOT",
    70: "TAZ",
    71: "ZAZ",
}


def plot_doc(df: pd.DataFrame, fig_location: str = None,
             show_figure: bool = False) -> pd.DataFrame:
    """ Škoda na vozidle (p53) dle výrobní značky (p45a)
        pro osobní automobily (p44 == 3). """

    # Kopie dataframe s daty pro osobní automobily (p44 == 3)
    df1 = df[["p45a", "p53"]][df["p44"] == 3].copy()

    # Odstranit nulové hodnoty p53
    df1 = df1[df1["p53"] > 0]

    # Odstranit neplatné značky
    df1 = df1[df1["p45a"].isin(CAR_BRANDS.keys())]

    # Převod na názvy výrobních značek
    df1["p45a"] = df1["p45a"].map(CAR_BRANDS)

    # Uložení počtu vozidel na výrobní značku
    p45a_count = df1["p45a"].value_counts()

    # Sloupec p53 je ve stokorunách.
    df1["p53"] *= 100

    # Agregace dle výrobní značky (p45a) a výpočet průměrné škody (p53)
    df1 = df1.groupby("p45a").agg({"p53": "mean"}).reset_index()

    # Mapování počtu nehod na značku
    df1["count"] = df1["p45a"].map(p45a_count)

    # Seřazení podle průměrné škody (p53)
    df1 = df1.sort_values("p53", ascending=False)

    # Vytvoření grafu
    fig, axes = plt.subplots(1, 2, figsize=(12, 10))
    axes = axes.flatten()

    # Vykreslení grafu
    g1 = sns.barplot(y="p45a", x="p53", data=df1, ax=axes[0], orient="h")
    g1.bar_label(g1.containers[0])

    g2 = sns.barplot(y="p45a", x="count", data=df1, ax=axes[1], orient="h")
    g2.bar_label(g2.containers[0])

    # Nastavení os
    axes[0].set_xlabel("Průměrná škoda [Kč]")
    axes[0].set_ylabel("Výrobní značka")
    axes[0].set_title("Výrobní značky seřazené podle průměrné škody")
    axes[0].set_xlim(right=df1["p53"].max() * 1.15)

    axes[1].set_xlabel("Počet nehod")
    axes[1].set_ylabel("Výrobní značka")
    axes[1].set_title("Počet nehod na výrobní značku")
    axes[1].set_xlim(right=df1["count"].max() * 1.15)

    # Zobrazení a uložení grafu
    fig.tight_layout()
    if show_figure:
        fig.show()
    if fig_location:
        fig.savefig(fig_location)

    return df1


def print_result(df: pd.DataFrame) -> None:
    """ Výpis výsledků. """

    # Výpis průměrné škody na výrobní značku
    print("Průměrná škoda na výrobní značku:")
    for _, row in df.iterrows():
        print(f"{row['p45a']}: {row['p53']:.2f} Kč")

    print("\n")

    # Výpis počtu nehod na výrobní značku
    print("\nPočet nehod na výrobní značku:")
    for _, row in df.iterrows():
        print(f"{row['p45a']}: {row['count']}")

# %%
if __name__ == "__main__":
    # %%
    df = pd.read_pickle("accidents.pkl.gz")
    # %%
    df1 = plot_doc(df, "fig.png", True)
    # %%
    print_result(df1)
