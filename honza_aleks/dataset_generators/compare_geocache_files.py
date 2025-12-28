import pandas as pd

print("="*70)
print("Porovnání cities_geocache.csv a cities_geocache_with_prijmy.csv")
print("="*70)

# Načtení dat
print("\n1. Načítám soubory...")
df_geocache = pd.read_csv('../data/cities_geocache.csv')
df_merged = pd.read_csv('../data/cities_geocache_with_prijmy.csv')

print(f"   ✓ cities_geocache.csv: {len(df_geocache)} obcí")
print(f"   ✓ cities_geocache_with_prijmy.csv: {len(df_merged)} obcí")

# Normalizace čísel obcí
print("\n2. Normalizuji čísla obcí...")
df_geocache['Cislo_normalized'] = df_geocache['Cislo_obce'].astype(
    float).astype(int)
df_merged['Cislo_normalized'] = df_merged['Cislo_obce'].astype(
    float).astype(int)

# Vytvoření setů pro porovnání
cisla_geocache = set(df_geocache['Cislo_normalized'])
cisla_merged = set(df_merged['Cislo_normalized'])

# Obce v geocache, ale ne v merged
print("\n" + "="*70)
print("OBCE V GEOCACHE, ALE NE V MERGED (nemají příjmy)")
print("="*70)
pouze_v_geocache = cisla_geocache - cisla_merged
if len(pouze_v_geocache) > 0:
    print(f"\nCelkem: {len(pouze_v_geocache)} obcí\n")
    df_pouze_geocache = df_geocache[df_geocache['Cislo_normalized'].isin(
        pouze_v_geocache)]
    df_pouze_geocache = df_pouze_geocache.sort_values('Cislo_normalized')

    # Zobrazíme první 50
    display_count = min(50, len(df_pouze_geocache))
    print(f"Prvních {display_count} obcí:")
    for _, row in df_pouze_geocache.head(display_count).iterrows():
        cislo = int(row['Cislo_normalized'])
        nazev = row['Nazev_obce']
        print(f"   {cislo}: {nazev}")

    if len(pouze_v_geocache) > display_count:
        print(
            f"\n   ... a dalších {len(pouze_v_geocache) - display_count} obcí")

    # Uložení do souboru
    output_file = '../data/obce_pouze_v_geocache.csv'
    df_pouze_geocache[['Cislo_obce', 'Nazev_obce', 'Kraj', 'Lat', 'Lon']].to_csv(
        output_file, index=False, encoding='utf-8-sig')
    print(f"\n   💾 Uloženo do: {output_file}")
else:
    print("\n   ✓ Žádné obce")

# Obce v merged, ale ne v geocache
print("\n" + "="*70)
print("OBCE V MERGED, ALE NE V GEOCACHE (mají příjmy, ale nemají souřadnice)")
print("="*70)
pouze_v_merged = cisla_merged - cisla_geocache
if len(pouze_v_merged) > 0:
    print(f"\nCelkem: {len(pouze_v_merged)} obcí\n")
    df_pouze_merged = df_merged[df_merged['Cislo_normalized'].isin(
        pouze_v_merged)]
    df_pouze_merged = df_pouze_merged.sort_values('Cislo_normalized')

    # Zobrazíme všechny (mělo by jich být málo)
    print("Seznam obcí:")
    for _, row in df_pouze_merged.iterrows():
        cislo = int(row['Cislo_normalized'])
        nazev = row['Nazev_obce_prijmy']
        lat = row['Lat']
        lon = row['Lon']
        coords = f"({lat}, {lon})" if pd.notna(
            lat) and pd.notna(lon) else "bez souřadnic"
        print(f"   {cislo}: {nazev} - {coords}")

    # Uložení do souboru
    output_file = '../data/obce_pouze_v_merged.csv'
    df_pouze_merged[['Cislo_obce', 'Nazev_obce_prijmy', 'Lat', 'Lon']].to_csv(
        output_file, index=False, encoding='utf-8-sig')
    print(f"\n   💾 Uloženo do: {output_file}")
else:
    print("\n   ✓ Žádné obce")

# Obce v obou souborech
print("\n" + "="*70)
print("STATISTIKY")
print("="*70)
spolecne = cisla_geocache & cisla_merged
print(f"\n   ✓ Obce v obou souborech: {len(spolecne)}")
print(f"   ✓ Pouze v geocache: {len(pouze_v_geocache)}")
print(f"   ✓ Pouze v merged: {len(pouze_v_merged)}")
print(f"   ✓ Celkem unikátních obcí: {len(cisla_geocache | cisla_merged)}")

# Ověříme obce bez souřadnic v merged
print("\n" + "="*70)
print("OBCE V MERGED BEZ SOUŘADNIC")
print("="*70)
bez_souradnic = df_merged[df_merged['Lat'].isna() | df_merged['Lon'].isna()]
if len(bez_souradnic) > 0:
    print(f"\nCelkem: {len(bez_souradnic)} obcí\n")
    print("Seznam prvních 30 obcí:")
    for _, row in bez_souradnic.head(30).iterrows():
        cislo = int(row['Cislo_normalized'])
        nazev = row['Nazev_obce_prijmy']
        print(f"   {cislo}: {nazev}")

    if len(bez_souradnic) > 30:
        print(f"\n   ... a dalších {len(bez_souradnic) - 30} obcí")

    # Uložení do souboru
    output_file = '../data/obce_bez_souradnic.csv'
    bez_souradnic[['Cislo_obce', 'Nazev_obce_prijmy', 'DPH', 'DPPO']].to_csv(
        output_file, index=False, encoding='utf-8-sig')
    print(f"\n   💾 Uloženo do: {output_file}")
else:
    print("\n   ✓ Všechny obce mají souřadnice!")

print("\n" + "="*70)
print("HOTOVO")
print("="*70)
