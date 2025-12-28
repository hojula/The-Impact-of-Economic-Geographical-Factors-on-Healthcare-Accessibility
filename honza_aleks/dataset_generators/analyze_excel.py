import pandas as pd

print("Analýza Excel souboru s daňovými příjmy")
print("="*70)

excel_file = '../data/Mesicni_danove_prijmy_obci_2025_10.xlsx'

# Načteme prvních 20 řádků bez headeru, abychom viděli strukturu
print("\n1. Prvních 20 řádků souboru (bez headeru):")
print("="*70)
df_raw = pd.read_excel(excel_file, header=None, nrows=20)
print(df_raw)

print("\n\n2. Počet sloupců:", len(df_raw.columns))
print("="*70)

# Zkusíme různé header pozice
print("\n3. Testování různých header pozic:")
print("="*70)
for i in range(8):
    print(f"\n--- Header na řádku {i} ---")
    try:
        df = pd.read_excel(excel_file, header=i, nrows=5)
        print(f"Sloupce ({len(df.columns)} celkem):")
        for idx, col in enumerate(df.columns):
            print(f"  {idx}: {col}")
        print(f"\nPrvní 2 řádky dat:")
        print(df.head(2))
    except Exception as e:
        print(f"Chyba: {e}")
