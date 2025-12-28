import pandas as pd
import numpy as np

print("="*70)
print("Spojování geocache s měsíčními daňovými příjmy obcí")
print("="*70)

# Načtení geocache
print("\n1. Načítám cities_geocache.csv...")
df_geocache = pd.read_csv('../data/cities_geocache.csv')
print(f"   ✓ Načteno {len(df_geocache)} obcí")
print(f"   Sloupce: {df_geocache.columns.tolist()}")

# Načtení měsíčních daňových příjmů
print("\n2. Načítám Mesicni_danove_prijmy_obci_2025_10.xlsx (list 01_2025)...")
# Header je na řádku 1 (druhý řádek, 0-indexed)
df_prijmy = pd.read_excel(
    '../data/Mesicni_danove_prijmy_obci_2025_10.xlsx', sheet_name='01_2025', header=1)
print(f"   ✓ Načteno {len(df_prijmy)} obcí")

# Zobrazíme názvy sloupců
print("\n3. Sloupce v Excel souboru:")
for i, col in enumerate(df_prijmy.columns):
    # Vytiskneme krátkou verzi názvu (první řádek)
    col_name = str(col).split('\n')[0]
    print(f"   {i}: {col_name}")

# Přejmenujeme sloupce na jednodušší názvy
print("\n4. Přejmenovávám sloupce...")
column_mapping = {
    'ČÍSLO OBCE': 'Cislo_obce',
    'NÁZEV OBCE': 'Nazev_obce_prijmy'
}

# Najdeme sloupce podle klíčových slov
for col in df_prijmy.columns:
    col_str = str(col)
    if 'DPH' in col_str and 'písm. b)' in col_str:
        column_mapping[col] = 'DPH'
    elif 'DNV' in col_str:
        column_mapping[col] = 'DNV'
    elif 'DPPO' in col_str:
        column_mapping[col] = 'DPPO'
    elif 'DPFO' in col_str and 'písm. e)' in col_str:
        column_mapping[col] = 'DPFO'
    elif 'DPFO srážkou' in col_str or 'DPFO - srážkou' in col_str:
        column_mapping[col] = 'DPFO_srazkou'
    elif 'DPFO - závislá činnost' in col_str and 'písm. c)' in col_str:
        column_mapping[col] = 'DPFO_zavisla_c'
    elif 'DPFO - závislá činnost' in col_str and 'písm. h)' in col_str:
        column_mapping[col] = 'DPFO_zavisla_h'

df_prijmy = df_prijmy.rename(columns=column_mapping)
print(f"   ✓ Přejmenováno {len(column_mapping)} sloupců")

# Identifikujeme daňové sloupce pro statistiky
tax_columns = ['DPH', 'DNV', 'DPPO', 'DPFO',
               'DPFO_srazkou', 'DPFO_zavisla_c', 'DPFO_zavisla_h']
available_tax_cols = [col for col in tax_columns if col in df_prijmy.columns]

print(f"\n5. Zachovávám všechny sloupce z Excelu")
print(f"   ✓ Celkem sloupců: {len(df_prijmy.columns)}")
print(f"   ✓ Daňové sloupce: {available_tax_cols}")

# Odfiltrujeme řádky s nečíselnými hodnotami v Cislo_obce (např. "Součet")
print("\n6. Odstraňuji nečíselné řádky (součty, atd.)...")
original_count = len(df_prijmy)
df_prijmy = df_prijmy[pd.to_numeric(
    df_prijmy['Cislo_obce'], errors='coerce').notna()]
removed_count = original_count - len(df_prijmy)
if removed_count > 0:
    print(f"   ✓ Odstraněno {removed_count} nečíselných řádků")
print(f"   ✓ Zbývá {len(df_prijmy)} platných obcí")

# Normalizace čísla obce pro spojení
print("\n7. Normalizuji čísla obcí...")
# Převedeme na int aby se odstranily .0 u floatů, pak na string
df_prijmy['Cislo_obce_normalized'] = df_prijmy['Cislo_obce'].astype(
    float).astype(int).astype(str).str.strip()
df_geocache['Cislo_obce_normalized'] = df_geocache['Cislo_obce'].astype(
    float).astype(int).astype(str).str.strip()

if 582573 in df_prijmy['Cislo_obce_normalized'].astype(int).values:
    print("   ✓ Úsobrno (582573) je v datech příjmů")
else:
    print("   ✗ Úsobrno (582573) NENÍ v datech příjmů")

# Speciální zpracování pro Prahu - sečteme všechny městské části
print("\n8. Speciální zpracování pro Prahu...")
# Praha má číslo 554782
praha_cislo = '554782'
# Najdeme všechny řádky, které obsahují "PRAHA" v názvu
praha_rows = df_prijmy[df_prijmy['Nazev_obce_prijmy'].str.contains(
    'PRAHA', case=False, na=False)]
if len(praha_rows) > 0:
    print(f"   ✓ Našel jsem {len(praha_rows)} pražských městských částí")
    # Sečteme všechny daňové příjmy pro Prahu
    praha_sum = {
        'Cislo_obce': praha_cislo,
        'Cislo_obce_normalized': praha_cislo,
        'Nazev_obce_prijmy': 'PRAHA'
    }
    for col in available_tax_cols:
        praha_sum[col] = praha_rows[col].sum()

    # Odstraníme všechny pražské městské části z df_prijmy
    df_prijmy = df_prijmy[~df_prijmy['Nazev_obce_prijmy'].str.contains(
        'PRAHA', case=False, na=False)]
    # Přidáme součet do df_prijmy
    df_prijmy = pd.concat(
        [df_prijmy, pd.DataFrame([praha_sum])], ignore_index=True)
    print(f"   ✓ Přidán součet pro Prahu (číslo {praha_cislo})")
    print(f"   Příklad: DPH = {praha_sum.get('DPH', 0):,.2f}")

# Speciální zpracování pro Ústí nad Labem - sečteme všechny městské části
print("\n8b. Speciální zpracování pro Ústí nad Labem...")
usti_cislo = '554804'
# Najdeme všechny řádky, které obsahují "ÚSTÍ NAD LABEM" v názvu
usti_rows = df_prijmy[df_prijmy['Nazev_obce_prijmy'].str.contains(
    'ÚSTÍ NAD LABEM', case=False, na=False)]
if len(usti_rows) > 0:
    print(f"   ✓ Našel jsem {len(usti_rows)} částí Ústí nad Labem")
    # Sečteme všechny daňové příjmy
    usti_sum = {
        'Cislo_obce': usti_cislo,
        'Cislo_obce_normalized': usti_cislo,
        'Nazev_obce_prijmy': 'ÚSTÍ NAD LABEM'
    }
    for col in available_tax_cols:
        usti_sum[col] = usti_rows[col].sum()

    # Odstraníme všechny části Ústí nad Labem z df_prijmy
    df_prijmy = df_prijmy[~df_prijmy['Nazev_obce_prijmy'].str.contains(
        'ÚSTÍ NAD LABEM', case=False, na=False)]
    # Přidáme součet do df_prijmy
    df_prijmy = pd.concat(
        [df_prijmy, pd.DataFrame([usti_sum])], ignore_index=True)
    print(f"   ✓ Přidán součet pro Ústí nad Labem (číslo {usti_cislo})")
    print(f"   Příklad: DPH = {usti_sum.get('DPH', 0):,.2f}")

# Speciální zpracování pro Pardubice - sečteme všechny městské části
print("\n8c. Speciální zpracování pro Pardubice...")
pardubice_cislo = '555134'
# Najdeme všechny řádky, které obsahují "PARDUBICE" v názvu
pardubice_rows = df_prijmy[df_prijmy['Nazev_obce_prijmy'].str.contains(
    'PARDUBICE', case=False, na=False)]
if len(pardubice_rows) > 0:
    print(f"   ✓ Našel jsem {len(pardubice_rows)} částí Pardubic")
    # Sečteme všechny daňové příjmy
    pardubice_sum = {
        'Cislo_obce': pardubice_cislo,
        'Cislo_obce_normalized': pardubice_cislo,
        'Nazev_obce_prijmy': 'PARDUBICE'
    }
    for col in available_tax_cols:
        pardubice_sum[col] = pardubice_rows[col].sum()

    # Odstraníme všechny části Pardubic z df_prijmy
    df_prijmy = df_prijmy[~df_prijmy['Nazev_obce_prijmy'].str.contains(
        'PARDUBICE', case=False, na=False)]
    # Přidáme součet do df_prijmy
    df_prijmy = pd.concat(
        [df_prijmy, pd.DataFrame([pardubice_sum])], ignore_index=True)
    print(f"   ✓ Přidán součet pro Pardubice (číslo {pardubice_cislo})")
    print(f"   Příklad: DPH = {pardubice_sum.get('DPH', 0):,.2f}")

# Speciální zpracování pro Plzeň - sečteme všechny městské části
print("\n8d. Speciální zpracování pro Plzeň...")
plzen_cislo = '554791'
# Najdeme všechny řádky, které obsahují "PLZEŇ" v názvu
plzen_rows = df_prijmy[df_prijmy['Nazev_obce_prijmy'].str.contains(
    'PLZEŇ', case=False, na=False)]
if len(plzen_rows) > 0:
    print(f"   ✓ Našel jsem {len(plzen_rows)} částí Plzně")
    # Sečteme všechny daňové příjmy
    plzen_sum = {
        'Cislo_obce': plzen_cislo,
        'Cislo_obce_normalized': plzen_cislo,
        'Nazev_obce_prijmy': 'PLZEŇ'
    }
    for col in available_tax_cols:
        plzen_sum[col] = plzen_rows[col].sum()

    # Odstraníme všechny části Plzně z df_prijmy
    df_prijmy = df_prijmy[~df_prijmy['Nazev_obce_prijmy'].str.contains(
        'PLZEŇ', case=False, na=False)]
    # Přidáme součet do df_prijmy
    df_prijmy = pd.concat(
        [df_prijmy, pd.DataFrame([plzen_sum])], ignore_index=True)
    print(f"   ✓ Přidán součet pro Plzeň (číslo {plzen_cislo})")
    print(f"   Příklad: DPH = {plzen_sum.get('DPH', 0):,.2f}")

# Speciální zpracování pro Ostravu - sečteme všechny městské části
print("\n8e. Speciální zpracování pro Ostravu...")
ostrava_cislo = '554821'
# Definujeme čísla obcí patřících k Ostravě
ostrava_obce = ['554308', '554324', '554332', '554367', '554375', '554430',
                '554537', '554561', '554570', '554588', '554669', '554685',
                '554715', '554723', '554219', '554227', '554235', '554243',
                '554286']
# Najdeme všechny řádky, které obsahují "OSTRAVA" nebo "PORUBA" v názvu, nebo mají specifické číslo obce
ostrava_rows = df_prijmy[
    df_prijmy['Nazev_obce_prijmy'].str.contains('OSTRAVA|PORUBA', case=False, na=False, regex=True) |
    df_prijmy['Cislo_obce_normalized'].isin(ostrava_obce)
]
if len(ostrava_rows) > 0:
    print(f"   ✓ Našel jsem {len(ostrava_rows)} částí Ostravy")
    # Sečteme všechny daňové příjmy
    ostrava_sum = {
        'Cislo_obce': ostrava_cislo,
        'Cislo_obce_normalized': ostrava_cislo,
        'Nazev_obce_prijmy': 'OSTRAVA'
    }
    for col in available_tax_cols:
        ostrava_sum[col] = ostrava_rows[col].sum()

    # Odstraníme všechny části Ostravy z df_prijmy
    df_prijmy = df_prijmy[
        ~(df_prijmy['Nazev_obce_prijmy'].str.contains('OSTRAVA|PORUBA', case=False, na=False, regex=True) |
          df_prijmy['Cislo_obce_normalized'].isin(ostrava_obce))
    ]
    # Přidáme součet do df_prijmy
    df_prijmy = pd.concat(
        [df_prijmy, pd.DataFrame([ostrava_sum])], ignore_index=True)
    print(f"   ✓ Přidán součet pro Ostravu (číslo {ostrava_cislo})")
    print(f"   Příklad: DPH = {ostrava_sum.get('DPH', 0):,.2f}")

# Speciální zpracování pro Brno - sečteme všechny městské části
print("\n8f. Speciální zpracování pro Brno...")
brno_cislo = '582786'
# Najdeme všechny řádky, které obsahují "BRNO" v názvu
brno_rows = df_prijmy[df_prijmy['Nazev_obce_prijmy'].str.contains(
    'BRNO', case=False, na=False)]
if len(brno_rows) > 0:
    print(f"   ✓ Našel jsem {len(brno_rows)} částí Brna")
    # Sečteme všechny daňové příjmy
    brno_sum = {
        'Cislo_obce': brno_cislo,
        'Cislo_obce_normalized': brno_cislo,
        'Nazev_obce_prijmy': 'BRNO'
    }
    for col in available_tax_cols:
        brno_sum[col] = brno_rows[col].sum()

    # Odstraníme všechny části Brna z df_prijmy
    df_prijmy = df_prijmy[~df_prijmy['Nazev_obce_prijmy'].str.contains(
        'BRNO', case=False, na=False)]
    # Přidáme součet do df_prijmy
    df_prijmy = pd.concat(
        [df_prijmy, pd.DataFrame([brno_sum])], ignore_index=True)
    print(f"   ✓ Přidán součet pro Brno (číslo {brno_cislo})")
    print(f"   Příklad: DPH = {brno_sum.get('DPH', 0):,.2f}")

# Speciální zpracování pro Opavu
print("\n8g. Speciální zpracování pro Opavu...")
opava_cislo = '505927'
# Definujeme čísla obcí patřících k Opavě
opava_obce = ['555339', '555355', '555371',
              '555401', '555410', '555436', '555461', '556700']
# Najdeme všechny řádky, které obsahují "OPAVA" v názvu nebo mají specifické číslo obce
opava_rows = df_prijmy[
    df_prijmy['Nazev_obce_prijmy'].str.contains('OPAVA', case=False, na=False) |
    df_prijmy['Cislo_obce_normalized'].isin(opava_obce)
]
if len(opava_rows) > 0:
    print(f"   ✓ Našel jsem {len(opava_rows)} částí Opavy")
    # Sečteme všechny daňové příjmy
    opava_sum = {
        'Cislo_obce': opava_cislo,
        'Cislo_obce_normalized': opava_cislo,
        'Nazev_obce_prijmy': 'OPAVA'
    }
    for col in available_tax_cols:
        opava_sum[col] = opava_rows[col].sum()

    # Odstraníme všechny části Opavy z df_prijmy
    df_prijmy = df_prijmy[
        ~(df_prijmy['Nazev_obce_prijmy'].str.contains('OPAVA', case=False, na=False) |
          df_prijmy['Cislo_obce_normalized'].isin(opava_obce))
    ]
    # Přidáme součet do df_prijmy
    df_prijmy = pd.concat(
        [df_prijmy, pd.DataFrame([opava_sum])], ignore_index=True)
    print(f"   ✓ Přidán součet pro Opavu (číslo {opava_cislo})")
    print(f"   Příklad: DPH = {opava_sum.get('DPH', 0):,.2f}")

# Speciální zpracování pro Liberec
print("\n8h. Speciální zpracování pro Liberec...")
liberec_cislo = '563889'
# Definujeme čísla obcí patřících k Liberci
liberec_obce = ['556891']
# Najdeme všechny řádky, které obsahují "LIBEREC" v názvu nebo mají specifické číslo obce
liberec_rows = df_prijmy[
    df_prijmy['Nazev_obce_prijmy'].str.contains('LIBEREC', case=False, na=False) |
    df_prijmy['Cislo_obce_normalized'].isin(liberec_obce)
]
if len(liberec_rows) > 0:
    print(f"   ✓ Našel jsem {len(liberec_rows)} částí Liberce")
    # Sečteme všechny daňové příjmy
    liberec_sum = {
        'Cislo_obce': liberec_cislo,
        'Cislo_obce_normalized': liberec_cislo,
        'Nazev_obce_prijmy': 'LIBEREC'
    }
    for col in available_tax_cols:
        liberec_sum[col] = liberec_rows[col].sum()

    # Odstraníme všechny části Liberce z df_prijmy
    df_prijmy = df_prijmy[
        ~(df_prijmy['Nazev_obce_prijmy'].str.contains('LIBEREC', case=False, na=False) |
          df_prijmy['Cislo_obce_normalized'].isin(liberec_obce))
    ]
    # Přidáme součet do df_prijmy
    df_prijmy = pd.concat(
        [df_prijmy, pd.DataFrame([liberec_sum])], ignore_index=True)
    print(f"   ✓ Přidán součet pro Liberec (číslo {liberec_cislo})")
    print(f"   Příklad: DPH = {liberec_sum.get('DPH', 0):,.2f}")

# Spojení dat - přidáme souřadnice z geocache k datům z Excelu
print("\n9. Spojuji data (přidávám souřadnice k Excelu)...")
# Vybereme jen souřadnice a číslo obce z geocache
geocache_coords = df_geocache[['Cislo_obce_normalized', 'Lat', 'Lon']].copy()

df_merged = df_prijmy.merge(
    geocache_coords,
    on='Cislo_obce_normalized',
    how='left'
)

# Odstraníme pomocný sloupec
df_merged = df_merged.drop(columns=['Cislo_obce_normalized'], errors='ignore')

# Statistiky
matched = df_merged[['Lat', 'Lon']].notna().all(axis=1).sum()
print(f"\n10. Výsledky spojení:")
print(f"   ✓ Celkem obcí v Excelu: {len(df_prijmy)}")
print(f"   ✓ Spojeno se souřadnicemi: {matched}")
print(f"   ✓ Bez souřadnic: {len(df_prijmy) - matched}")
print(f"   ✓ Úspěšnost: {matched/len(df_prijmy)*100:.1f}%")

# Uložení
output_file = '../data/cities_geocache_with_prijmy.csv'
df_merged.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n11. ✓ Uloženo do: {output_file}")

# Přehled finálních sloupců
print(f"\nFinální struktura:")
print(f"   ✓ Celkem sloupců: {len(df_merged.columns)}")
print(f"   ✓ Ukázka sloupců: {df_merged.columns.tolist()[:10]}...")

# Ukázka dat
print(f"\nUkázka prvních 3 obcí:")
display_cols = ['Cislo_obce', 'Nazev_obce_prijmy'] + \
    available_tax_cols + ['Lat', 'Lon']
# Filtrujeme jen sloupce, které existují
display_cols = [col for col in display_cols if col in df_merged.columns]
print(df_merged[display_cols].head(3).to_string())

print("\n" + "="*70)
print("Hotovo!")
print("="*70)
