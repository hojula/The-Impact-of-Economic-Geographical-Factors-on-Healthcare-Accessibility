import pandas as pd
import glob
import os

def spojit_excely_final():
    soubory = glob.glob("okresy/*.xlsx")
    vsechna_data = []
    
    print(f"Nalezeno {len(soubory)} souborů. Začínám zpracování...")

    # Definice sloupců (index 0 bude Obec, index 1-13 data)
    nove_sloupce = [
        'Obec', 
        '0-14_let_celkem', '0-14_let_muzi', '0-14_let_zeny',
        '15-64_let_celkem', '15-64_let_muzi', '15-64_let_zeny',
        '65+_let_celkem', '65+_let_muzi', '65+_let_zeny',
        'Prumerny_vek_celkem', 'Prumerny_vek_muzi', 'Prumerny_vek_zeny',
        'Index_stari'
    ]

    for soubor in soubory:
        try:
            # Načteme celý excel bez hlavičky
            df_raw = pd.read_excel(soubor, header=None)
            
            # 1. Získání názvu okresu
            nazev_okresu = os.path.splitext(soubor)[0]
            
            start_row_index = -1
            
            # Hledáme začátek (řádek s "v tom obce:")
            # Hledáme i název okresu uvnitř souboru pro hezčí výstup
            for i in range(min(30, len(df_raw))):
                val_col1 = str(df_raw.iloc[i, 1]) # Sloupec B
                
                if "Okres " in val_col1:
                    nazev_okresu = val_col1.strip()
                
                if "v tom obce:" in val_col1:
                    start_row_index = i + 1
                    break
            
            if start_row_index == -1:
                print(f"POZOR: V souboru {soubor} nebyl nalezen začátek dat, přeskakuji.")
                continue

            # 2. Ořízneme data od začátku dolů a vybereme správné sloupce (B až O)
            df_clean = df_raw.iloc[start_row_index:].iloc[:, 1:15].copy()
            df_clean.columns = nove_sloupce

            # --- NOVÁ ČÁST: HLEDÁNÍ KONCE (Kód:) ---
            end_row_index = -1
            
            # Projdeme sloupec 'Obec' a hledáme kde začíná patička
            # Resetujeme index, abychom mohli iterovat od 0
            df_clean = df_clean.reset_index(drop=True)
            
            for i in range(len(df_clean)):
                hodnota_obec = str(df_clean.at[i, 'Obec']).strip()
                
                # Pokud narazíme na "Kód:", nebo prázdný řádek následovaný legendou
                if hodnota_obec.startswith("Kód:"):
                    end_row_index = i
                    break
            
            # Pokud jsme našli konec, ořízneme tabulku
            if end_row_index != -1:
                df_clean = df_clean.iloc[:end_row_index]
            
            # ---------------------------------------

            # Vyčistíme prázdné řádky, které mohly zbýt
            df_clean = df_clean.dropna(subset=['Obec'])
            
            # Přidáme sloupec s okresem
            df_clean.insert(0, 'Okres', nazev_okresu)

            vsechna_data.append(df_clean)
            print(f"Zpracováno: {soubor} ({nazev_okresu}) - {len(df_clean)} obcí")

        except Exception as e:
            print(f"CHYBA u souboru {soubor}: {e}")

    # Spojení a uložení
    if vsechna_data:
        vysledny_df = pd.concat(vsechna_data, ignore_index=True)
        # vysledny_df.to_excel("KOMPLETNI_DATA_FINAL.xlsx", index=False)
        vysledny_df.to_csv("KOMPLETNI_DATA_FINAL.csv", index=False)
        print("\nHotovo! Vytvořen soubor 'KOMPLETNI_DATA_FINAL.xlsx'")
    else:
        print("Žádná data nebyla spojena.")

if __name__ == "__main__":
    spojit_excely_final()