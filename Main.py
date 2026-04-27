import pandas as pd
import numpy as np

# ============================================================
# PARTE 1 — CREAZIONE DATASET LOCALI
# ============================================================

# Seed per replicabilità risultati
np.random.seed(3)

# ORDINI (100k righe)
n_ordini = 100_000
ordini = pd.DataFrame({
    "ClienteID": np.random.randint(1, 5001, size=n_ordini),
    "ProdottoID": np.random.randint(1, 21, size=n_ordini),
    "Quantità": np.random.randint(1, 6, size=n_ordini),
    "DataOrdine": pd.date_range("2023-01-01", periods=n_ordini, freq="H")
})

ordini.to_csv("ordini.csv", index=False)


# Creazione PRODOTTI (20 prodotti)
prodotti = pd.DataFrame({
    "ProdottoID": range(1, 21),
    "Categoria": np.random.choice(["Elettronica", "Casa", "Sport", "Moda"], size=20),
    "Fornitore": np.random.choice(["Amazon", "eBay", "Zalando", "Decathlon"], size=20),
    "Prezzo": np.random.uniform(5, 300, size=20).round(2)
})

prodotti.to_json("prodotti.json", orient="records")


# Creazione CLIENTI (5000 clienti)
clienti = pd.DataFrame({
    "ClienteID": range(1, 5001),
    "Regione": np.random.choice(["Nord", "Centro", "Sud", "Isole"], size=5000),
    "Segmento": np.random.choice(["Retail", "Corporate", "Small_Business"], size=5000)
})

clienti.to_csv("clienti.csv", index=False)

# ============================================================
# PARTE 2 — DATAFRAME UNIFICATO
# ============================================================

# Carica ordini
df_ordini = pd.read_csv("ordini.csv", parse_dates=["DataOrdine"])

# Carica prodotti
df_prodotti = pd.read_json("prodotti.json")

# Carica clienti
df_clienti = pd.read_csv("clienti.csv")

# Merge dati:
df = (
    df_ordini
    .merge(df_prodotti, on="ProdottoID", how="left")
    .merge(df_clienti, on="ClienteID", how="left")
)

# ============================================================
# PARTE 3 — OTTIMIZZAZIONE TIPI
# ============================================================

# calcolo memoria utilizzata prima delle ottimizzazioni
memory_init = df.memory_usage(deep=True).sum() / 1024**2

# Downcast numerici
df["ClienteID"] = pd.to_numeric(df["ClienteID"], downcast="integer")
df["ProdottoID"] = pd.to_numeric(df["ProdottoID"], downcast="integer")
df["Quantità"]   = pd.to_numeric(df["Quantità"],   downcast="integer")
df["Prezzo"] = df["Prezzo"].astype('float64')

# Categorical per colonne ripetitive
for col in ["Categoria", "Fornitore", "Regione", "Segmento"]:
    df[col] = df[col].astype("category")

# Benchmark prima e dopo ottimizzazioni:
memory_final = df.memory_usage(deep=True).sum() / 1024**2

print("----- BENCHMARK OTTIMIZZAZIONI -----")
print(f"Memoria Iniziale: {memory_init:.2f} MB")
print(f"Memoria Finale: {memory_final:.2f} MB")
print(f"Risparmio memoria: {(memory_init - memory_final):.2f} MB")

# ============================================================
# PARTE 4 — COLONNE CALCOLATE + FILTRI
# ============================================================

# Colonna calcolata
df["ValoreTotale"] = df["Prezzo"] * df["Quantità"]
df["ValoreTotale"] = df["ValoreTotale"].astype('float64')

# Check dati
df.info()

# Filtri valore > 100, Segmento Clienti
df_filtrato = df[
    (df["ValoreTotale"] > 100) &
    (df["Segmento"] == "Small_Business")
]

print("\n---- DF FILTRATO ----")
df_filtrato.info()

# =============================================
# EXTRA: Grafico Seaborn, vendite per categoria
# =============================================

import seaborn as sns
import matplotlib.pyplot as plt

# GRAFICO - BARPLOT VENDITE TOTALI PER CATEGORIA

# Aggregazione vendite
vendite_categoria = (
    df.groupby("Categoria")["ValoreTotale"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

# Normalizzazione valori - scala in Milioni di €
vendite_categoria["ValoreTotale_Mln"] = vendite_categoria["ValoreTotale"] / 1_000_000

plt.figure(figsize=(10, 6))

sns.barplot(
    data=vendite_categoria,
    x="Categoria",
    y="ValoreTotale_Mln",
    palette="YlGn"
)

plt.title("Vendite Totali per Categoria", fontsize=14, pad=15)
plt.xlabel("Categoria")
plt.ylabel("Vendite Totali (Mln.€)")
plt.xticks(rotation=20)
plt.tight_layout()
plt.show()


# GRAFICO 2 — DONUT CHART PER SEGMENTO CLIENTI

segmenti = df["Segmento"].value_counts()

plt.figure(figsize=(7, 7))

# Palette YlGn con numero di segmenti
colori = sns.color_palette("Accent", n_colors=len(segmenti))

patches, texts, autotexts = plt.pie(
    segmenti.values,
    labels=segmenti.index,
    autopct='%1.1f%%',
    startangle=140,
    colors=colori,
    pctdistance=0.85
)

# Donut
plt.gca().add_artist(plt.Circle((0, 0), 0.60, color='white'))

plt.title("Distribuzione Clienti per Segmento", fontsize=14, pad=20)
plt.tight_layout()
plt.show()