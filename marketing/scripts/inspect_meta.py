import pandas as pd
import sys

filepath = "marketing/meta/exports/meta_export_20260602.csv"

try:
    df = pd.read_csv(filepath, encoding="utf-16", sep="\t", low_memory=False)
    print(f"Filas: {len(df)}, Columnas: {len(df.columns)}")
    print("\nColumnas clave encontradas:")
    key_cols = ["Campaign Name", "Campaign Status", "Ad Set Name", "Ad Set Run Status",
                "Ad Name", "Ad Status", "Countries", "Gender", "Age Min", "Age Max",
                "Publisher Platforms", "Optimization Goal", "Ad Set Daily Budget",
                "Campaign Daily Budget", "Body", "Title", "Call to Action"]
    for col in key_cols:
        if col in df.columns:
            print(f"  OK: {col}")

    print("\n--- CAMPANAS ---")
    camp_cols = [c for c in df.columns if "Campaign" in c]
    print(", ".join(camp_cols[:10]))

    print("\nNombres de campanas:")
    if "Campaign Name" in df.columns:
        camps = df["Campaign Name"].dropna().unique()
        for c in camps:
            print(f"  - {c}")

    print("\nEstado campanas:")
    if "Campaign Status" in df.columns:
        print(df["Campaign Status"].value_counts().to_string())

    print("\n--- CONJUNTOS DE ANUNCIOS ---")
    if "Ad Set Name" in df.columns:
        sets = df["Ad Set Name"].dropna().unique()
        for s in sets:
            print(f"  - {s}")

    print("\nEstado conjuntos:")
    if "Ad Set Run Status" in df.columns:
        print(df["Ad Set Run Status"].value_counts().to_string())

    print("\n--- ANUNCIOS ---")
    if "Ad Name" in df.columns:
        ads = df["Ad Name"].dropna().unique()
        for a in ads:
            print(f"  - {a}")

    print("\n--- SEGMENTACION ---")
    if "Countries" in df.columns:
        print("Paises:", df["Countries"].dropna().unique())
    if "Gender" in df.columns:
        print("Genero:", df["Gender"].dropna().unique())
    if "Age Min" in df.columns and "Age Max" in df.columns:
        print("Edad:", df[["Age Min","Age Max"]].dropna().drop_duplicates().to_string(index=False))

    print("\n--- OBJETIVO Y PRESUPUESTO ---")
    if "Campaign Objective" in df.columns:
        print("Objetivo:", df["Campaign Objective"].dropna().unique())
    if "Optimization Goal" in df.columns:
        print("Optimizacion:", df["Optimization Goal"].dropna().unique())
    if "Ad Set Daily Budget" in df.columns:
        print("Presupuesto diario Ad Set:", df["Ad Set Daily Budget"].dropna().unique())
    if "Campaign Daily Budget" in df.columns:
        print("Presupuesto diario Campana:", df["Campaign Daily Budget"].dropna().unique())

    print("\n--- COPIES (Body) ---")
    if "Body" in df.columns:
        bodies = df["Body"].dropna().unique()
        for b in bodies[:5]:
            print(f"\n  COPY: {str(b)[:300]}")

    print("\n--- TITULOS ---")
    if "Title" in df.columns:
        titles = df["Title"].dropna().unique()
        for t in titles:
            print(f"  - {t}")

    print("\n--- PLATAFORMAS ---")
    if "Publisher Platforms" in df.columns:
        print(df["Publisher Platforms"].dropna().unique())
    if "Facebook Positions" in df.columns:
        print("FB:", df["Facebook Positions"].dropna().unique())
    if "Instagram Positions" in df.columns:
        print("IG:", df["Instagram Positions"].dropna().unique())

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
