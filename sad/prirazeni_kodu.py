import pandas as pd

def pripojit_kody_fix():
    print("Načítám data...")
    
    # 1. NAČTENÍ
    try:
        # Zde zadejte název vašeho souboru s daty obcí
        df_main = pd.read_csv('vek_obec.csv') 
        ciselnik_okresy = pd.read_csv('CIS0109_CS.csv', encoding='utf-8')
        cities_geo = pd.read_csv('../data/cities_geocache.csv', encoding='utf-8')
    except FileNotFoundError as e:
        print(f"Chyba: {e}")
        return

    # 2. PŘÍPRAVA ČÍSELNÍKU (Název -> Kód)
    mapa_okresu = pd.Series(ciselnik_okresy.chodnota.values, index=ciselnik_okresy.text).to_dict()
    
    # Přidáme ruční pojistky pro Prahu (časté odlišnosti v názvech)
    if 'Praha' in mapa_okresu:
        mapa_okresu['Hlavní město Praha'] = mapa_okresu['Praha']
    
    # 3. OPRAVA A ČIŠTĚNÍ NÁZVŮ OKRESŮ VE VAŠICH DATECH
    # Odstraníme "Okres " ze začátku
    df_main['Okres_pro_parovani'] = df_main['Okres'].astype(str).str.replace('Okres ', '', regex=False).str.strip()
    
    # --- ZDE JE TA OPRAVA ---
    # Sjednotíme zápis "Praha - východ" na "Praha-východ" (odstranění mezer kolem pomlčky)
    df_main['Okres_pro_parovani'] = df_main['Okres_pro_parovani'].str.replace(' - ', '-', regex=False)
    
    # Pro jistotu explicitní přepis, pokud tam jsou nějaké divné znaky
    # Pokud název obsahuje "Praha" a "východ", přepíšeme natvrdo na klíč z číselníku
    maska_vychod = df_main['Okres_pro_parovani'].str.contains('Praha.*východ', regex=True, case=False)
    df_main.loc[maska_vychod, 'Okres_pro_parovani'] = 'Praha-východ'

    maska_zapad = df_main['Okres_pro_parovani'].str.contains('Praha.*západ', regex=True, case=False)
    df_main.loc[maska_zapad, 'Okres_pro_parovani'] = 'Praha-západ'
    
    # Stejná logika pro "Brno-město" a "Brno-venkov", kdyby náhodou
    df_main.loc[df_main['Okres_pro_parovani'].str.contains('Brno.*město', regex=True, case=False), 'Okres_pro_parovani'] = 'Brno-město'
    df_main.loc[df_main['Okres_pro_parovani'].str.contains('Brno.*venkov', regex=True, case=False), 'Okres_pro_parovani'] = 'Brno-venkov'

    # 4. PŘIŘAZENÍ KÓDU OKRESU
    df_main['Kod_Okresu'] = df_main['Okres_pro_parovani'].map(mapa_okresu)

    # Kontrolní výpis - které okresy se stále nepodařilo najít?
    chybejici_okresy = df_main[df_main['Kod_Okresu'].isna()]['Okres_pro_parovani'].unique()
    if len(chybejici_okresy) > 0:
        print(f"VAROVÁNÍ: Stále nemohu najít kód pro tyto okresy: {chybejici_okresy}")
        print("Zkontrolujte přesně názvy v souboru CIS0109_CS.csv")
    else:
        print("Všechny okresy úspěšně spárovány na kódy (CZ...).")

    # 5. SPOJENÍ S GEOCACHE DATY (přes Kód okresu a Název obce)
    df_main['Obec'] = df_main['Obec'].astype(str).str.strip()
    cities_geo['Nazev_obce'] = cities_geo['Nazev_obce'].astype(str).str.strip()
    cities_geo['Okres'] = cities_geo['Okres'].astype(str).str.strip()

    vysledek = pd.merge(
        df_main,
        cities_geo[['Okres', 'Nazev_obce', 'key', 'Cislo_obce']],
        left_on=['Kod_Okresu', 'Obec'],
        right_on=['Okres', 'Nazev_obce'],
        how='left'
    )

    # Úklid
    vysledek = vysledek.drop(columns=['Okres_pro_parovani', 'Okres_y', 'Nazev_obce'])
    if 'Okres_x' in vysledek.columns:
        vysledek = vysledek.rename(columns={'Okres_x': 'Okres'})
    
    # Vyčištění formátu key (z 123.0 na 123)
    vysledek['key'] = pd.to_numeric(vysledek['key'], errors='coerce').fillna(0).astype(int).astype(str).replace('0', '')

    # Uložení
    vysledek.to_csv("vek_obec_komplet_fixed.csv", index=False, encoding='utf-8-sig')
    
    # Finální statistika
    pocet_chyb = vysledek['key'].eq('').sum()
    print(f"\nHotovo. Počet obcí bez nalezeného ID: {pocet_chyb} z {len(vysledek)}")
    
    # Pokud stále chybí, vypíšeme ukázku, abychom věděli proč
    if pocet_chyb > 0:
        print("Ukázka obcí, kde se nepodařilo najít ID:")
        print(vysledek[vysledek['key'] == ''][['Okres', 'Obec']].head(10))

if __name__ == "__main__":
    pripojit_kody_fix()