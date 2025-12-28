import pandas as pd
import numpy as np
import time
import requests
import json
from pathlib import Path

# -------------------- Haversine --------------------


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # km
    lat1_rad, lon1_rad = np.radians(lat1), np.radians(lon1)
    lat2_rad, lon2_rad = np.radians(lat2), np.radians(lon2)
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = np.sin(dlat/2)**2 + np.cos(lat1_rad)*np.cos(lat2_rad)*np.sin(dlon/2)**2
    c = 2*np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R*c


# -------------------- Geokodér (Nominatim OSM) --------------------
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "Mozilla/5.0 (compatible; CzechMunicipalityGeocode/1.0; +https://github.com/hojula/SAN-final-project)"


def geocode_name(name, country_hint="Czechia", okres=""):
    """
    Vrátí (lat, lon, kraj) pro daný název obce. Používá Nominatim.
    Dodržuje 1 req/s a vrací None, None, None při neúspěchu.
    """
    # Sestavíme dotaz s okresem, pokud je k dispozici
    # Pro Prahu okres nepřidáváme
    if okres and name.lower() != "praha":
        query = f"{name}, {okres}, {country_hint}"
    else:
        query = f"{name}, {country_hint}" if country_hint else name

    params = {
        "q": query,
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
    }
    try:
        print(f"[Geocode] Hledám: '{query}'")
        r = requests.get(NOMINATIM_URL, params=params, headers={
                         "User-Agent": USER_AGENT}, timeout=20)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list) and len(data) > 0:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            # Zkusíme získat kraj z address details
            address = data[0].get("address", {})
            kraj = address.get("state") or address.get(
                "region") or address.get("county") or ""
            print(f"[Geocode] Úspěch: {lat}, {lon}, kraj={kraj}")
            return lat, lon, kraj
        else:
            print(f"[Geocode] Žádné výsledky pro '{query}'")
            return None, None, None
    except Exception as e:
        print(f"[Geocode] Selhalo pro '{query}': {e}")
        return None, None, None
    finally:
        # Nominatim fair use: max ~1 req/s
        time.sleep(1.0)


# -------------------- Jednoduchý cache pro geokódování --------------------
CACHE_PATH = Path("../data/cities_geocache.csv")


def load_cache():
    if CACHE_PATH.exists():
        df = pd.read_csv(CACHE_PATH)
        # Přidáme sloupec Cislo_obce, Kraj a Okres, pokud neexistují
        if "Cislo_obce" not in df.columns:
            df["Cislo_obce"] = ""
        if "Kraj" not in df.columns:
            df["Kraj"] = ""
        if "Okres" not in df.columns:
            df["Okres"] = ""
        # Klíč je číslo obce (pokud existuje), jinak název + okres
        if "key" not in df.columns:
            df["key"] = df["Cislo_obce"].astype(str).str.strip()
        return df[["key", "Cislo_obce", "Nazev_obce", "Country", "Kraj", "Okres", "Lat", "Lon"]].dropna(subset=["Lat", "Lon"])
    return pd.DataFrame(columns=["key", "Cislo_obce", "Nazev_obce", "Country", "Kraj", "Okres", "Lat", "Lon"])


def save_cache(df_cache):
    df_cache = df_cache.drop_duplicates(subset=["key"])
    df_cache.to_csv(CACHE_PATH, index=False, encoding="utf-8-sig")


def cache_key(cislo_obce):
    """Klíč do cache je číslo obce"""
    return str(cislo_obce).strip()


# -------------------- Načtení nemocnic z GeoJSON --------------------
def load_hospitals_from_geojson(geojson_path):
    """
    Načte nemocnice z GeoJSON souboru.
    Vrací DataFrame s názvy nemocnic a jejich souřadnicemi.
    """
    try:
        with open(geojson_path, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)

        hospitals = []
        for feature in geojson_data.get('features', []):
            props = feature.get('properties', {})
            geom = feature.get('geometry', {})
            coords = geom.get('coordinates', [])

            if len(coords) >= 2:
                # Vezme jen první část před čárkou
                name = props.get('title', '').split(',')[0].strip()
                lon, lat = coords[0], coords[1]
                hospitals.append({
                    'Nazev_nemocnice': name,
                    'Lat': lat,
                    'Lon': lon
                })

        return pd.DataFrame(hospitals)
    except Exception as e:
        print(f"Chyba při načítání GeoJSON: {e}")
        return pd.DataFrame(columns=['Nazev_nemocnice', 'Lat', 'Lon'])


# -------------------- Seznam nemocnic --------------------
geojson_cesta = '../data/mapanemocnic-mapa-nemocnic-v-cr.geojson'
df_nemocnice = load_hospitals_from_geojson(geojson_cesta)

if df_nemocnice.empty:
    print("--- VAROVÁNÍ: Nepodařilo se načíst nemocnice z GeoJSON, používám ukázkový seznam ---")
    data_nemocnic = {
        'Nazev_nemocnice': ['FN Ostrava', 'Nemocnice Rudná', 'IKEM Praha', 'Nemocnice Na Homolce'],
        'Lat': [49.8298, 49.8166, 50.0270, 50.0598],
        'Lon': [18.1633, 18.1402, 14.4757, 14.3725]
    }
    df_nemocnice = pd.DataFrame(data_nemocnic)

print(f"--- Načteno {len(df_nemocnice)} nemocnic ---")
print(df_nemocnice.head(10), "\n")

# -------------------- Načtení obcí --------------------
cesta_k_souboru = '../data/1300722503.xlsx'
df_obce = None

try:
    # Zkusíme načíst jako Excel soubor
    df_obce = pd.read_excel(cesta_k_souboru, header=4)
    print(
        f"--- Úspěšně načten váš soubor '{cesta_k_souboru}' (Excel) ---")
except Exception as e:
    print(f"CHYBA: Selhalo načítání souboru {cesta_k_souboru}. Chyba: {e}")
    df_obce = pd.DataFrame(columns=['Name of municipality'])

# normalizace názvů sloupců - přejmenujeme jen specifické sloupce, ale ZACHOVÁME všechny ostatní
rename_map = {}
if 'Name of municipality' in df_obce.columns:
    rename_map['Name of municipality'] = 'Nazev_obce'
else:
    # když není očekávaný sloupec, zkusíme najít podobné názvy
    for cand in ["Nazev_obce", "Obec", "Municipality", "Name", "Název obce"]:
        if cand in df_obce.columns:
            rename_map[cand] = 'Nazev_obce'
            break

# Zkusíme najít sloupec s okresem
for cand in ["District", "Okres", "district"]:
    if cand in df_obce.columns:
        rename_map[cand] = 'Okres'
        break

# Zkusíme najít sloupec s číslem obce
for cand in ["Code of municipality", "Cislo_obce", "Číslo obce", "Kod obce", "code", "municipality"]:
    if cand in df_obce.columns:
        rename_map[cand] = 'Cislo_obce'
        break

if rename_map:
    df_obce = df_obce.rename(columns=rename_map)

print(f"Zachovány VŠECHNY sloupce z Excelu: {len(df_obce.columns)} sloupců")

print("Nalezeny sloupce (prvních 5 řádků):")
print(df_obce.head(), "\n")

# -------------------- Příprava dat a doplnění souřadnic --------------------
# Ujistíme se, že máme sloupec Nazev_obce
if 'Nazev_obce' not in df_obce.columns:
    print("--- VAROVÁNÍ: Nebyl nalezen sloupec s názvy obcí. Použiji UKÁZKOVÁ data. ---")
    df_pro_vypocet = pd.DataFrame({
        'Nazev_obce': ['Praha', 'Benešov', 'Vřesina', 'Závada', 'Čavisov'],
        'Lat': [50.0755, 49.7820, 49.8542, 49.9298, 49.8335],
        'Lon': [14.4378, 14.6868, 18.1501, 18.0202, 18.1180],
        'Country': ['Czechia']*5
    })
else:
    df_pro_vypocet = df_obce.copy()
    # make dataset smaller
    # df_pro_vypocet = df_pro_vypocet.head(20)

    # Pokud nemáme sloupec Country, doplníme jako Czechia (lze změnit dle potřeby)
    if 'Country' not in df_pro_vypocet.columns:
        df_pro_vypocet['Country'] = 'Czechia'

    # Odstraníme řádky bez názvu obce
    df_pro_vypocet = df_pro_vypocet.dropna(subset=['Nazev_obce'])
    df_pro_vypocet['Nazev_obce'] = df_pro_vypocet['Nazev_obce'].astype(
        str).str.strip()

    # Pokud máme sloupec Okres, zpracujeme ho
    if 'Okres' in df_pro_vypocet.columns:
        df_pro_vypocet['Okres'] = df_pro_vypocet['Okres'].astype(
            str).str.strip()
        # Nahradíme NaN hodnotami prázdným řetězcem
        df_pro_vypocet['Okres'] = df_pro_vypocet['Okres'].replace('nan', '')
    else:
        df_pro_vypocet['Okres'] = ''

    # Pokud máme sloupec Cislo_obce, zpracujeme ho
    if 'Cislo_obce' in df_pro_vypocet.columns:
        df_pro_vypocet['Cislo_obce'] = df_pro_vypocet['Cislo_obce'].astype(
            str).str.strip()
        df_pro_vypocet['Cislo_obce'] = df_pro_vypocet['Cislo_obce'].replace(
            'nan', '')
    else:
        df_pro_vypocet['Cislo_obce'] = ''

    # Load cache
    df_cache = load_cache()

    # Zjistíme, které řádky nemají Lat/Lon
    need_geo_mask = (~df_pro_vypocet.columns.isin(['Lat', 'Lon']).any()) \
        or df_pro_vypocet.get('Lat').isna().any() \
        or df_pro_vypocet.get('Lon').isna().any()

    if 'Lat' not in df_pro_vypocet.columns:
        df_pro_vypocet['Lat'] = np.nan
    if 'Lon' not in df_pro_vypocet.columns:
        df_pro_vypocet['Lon'] = np.nan

    if need_geo_mask:
        print("--- Chybí souřadnice: pokusím se je doplnit z mapového API (Nominatim) ---")

        to_fill_idx = df_pro_vypocet.index[df_pro_vypocet['Lat'].isna(
        ) | df_pro_vypocet['Lon'].isna()]
        new_cache_rows = []

        # Počítadlo pro průběžné ukládání
        processed_count = 0
        vystupni_soubor = '../data/cities_hospital_distances.csv'

        for idx in to_fill_idx:
            name = df_pro_vypocet.at[idx, 'Nazev_obce']
            country = df_pro_vypocet.at[idx,
                                        'Country'] if 'Country' in df_pro_vypocet.columns else 'Czechia'
            okres = df_pro_vypocet.at[idx,
                                      'Okres'] if 'Okres' in df_pro_vypocet.columns else ''
            cislo_obce = df_pro_vypocet.at[idx,
                                           'Cislo_obce'] if 'Cislo_obce' in df_pro_vypocet.columns else ''
            key = cache_key(
                cislo_obce) if cislo_obce else f"name_{name}_{okres}"

            # 1) Zkus cache
            row_cache = df_cache[df_cache['key'] == key]
            if not row_cache.empty:
                lat = float(row_cache.iloc[0]['Lat'])
                lon = float(row_cache.iloc[0]['Lon'])
                kraj = row_cache.iloc[0].get('Kraj', '')
                cached_okres = row_cache.iloc[0].get('Okres', '')
                df_pro_vypocet.at[idx, 'Lat'] = lat
                df_pro_vypocet.at[idx, 'Lon'] = lon
                if 'Kraj' not in df_pro_vypocet.columns:
                    df_pro_vypocet['Kraj'] = ''
                df_pro_vypocet.at[idx, 'Kraj'] = kraj
                # Pokud okres není v Excel souboru, použijeme z cache
                if not okres and cached_okres:
                    df_pro_vypocet.at[idx, 'Okres'] = cached_okres

                # Spočítáme nejbližší nemocnici i pro data z cache
                min_dist, best_hospital = np.inf, None
                for _, nem in df_nemocnice.iterrows():
                    dist = haversine_distance(lat, lon, nem['Lat'], nem['Lon'])
                    if dist < min_dist:
                        min_dist = dist
                        best_hospital = nem['Nazev_nemocnice']

                if 'Nejblizsi_nemocnice' not in df_pro_vypocet.columns:
                    df_pro_vypocet['Nejblizsi_nemocnice'] = None
                if 'Vzdalenost_km' not in df_pro_vypocet.columns:
                    df_pro_vypocet['Vzdalenost_km'] = None

                df_pro_vypocet.at[idx, 'Nejblizsi_nemocnice'] = best_hospital
                df_pro_vypocet.at[idx, 'Vzdalenost_km'] = min_dist
                continue

            # 2) Geocode call - s okresem pro přesnější vyhledání
            lat, lon, kraj = geocode_name(
                name, country_hint=country, okres=okres)
            if lat is not None and lon is not None:
                df_pro_vypocet.at[idx, 'Lat'] = lat
                df_pro_vypocet.at[idx, 'Lon'] = lon
                if 'Kraj' not in df_pro_vypocet.columns:
                    df_pro_vypocet['Kraj'] = ''
                df_pro_vypocet.at[idx, 'Kraj'] = kraj if kraj else ''

                # Hned spočítáme nejbližší nemocnici pro tuto obec
                min_dist, best_hospital = np.inf, None
                for _, nem in df_nemocnice.iterrows():
                    dist = haversine_distance(lat, lon, nem['Lat'], nem['Lon'])
                    if dist < min_dist:
                        min_dist = dist
                        best_hospital = nem['Nazev_nemocnice']

                # Přidáme sloupce, pokud neexistují
                if 'Nejblizsi_nemocnice' not in df_pro_vypocet.columns:
                    df_pro_vypocet['Nejblizsi_nemocnice'] = None
                if 'Vzdalenost_km' not in df_pro_vypocet.columns:
                    df_pro_vypocet['Vzdalenost_km'] = None

                df_pro_vypocet.at[idx, 'Nejblizsi_nemocnice'] = best_hospital
                df_pro_vypocet.at[idx, 'Vzdalenost_km'] = min_dist

                new_cache_rows.append({
                    "key": key, "Cislo_obce": cislo_obce, "Nazev_obce": name, "Country": country, "Kraj": kraj if kraj else '', "Okres": okres, "Lat": lat, "Lon": lon
                })
                print(
                    f"+++ Geokódováno: '{name}' -> ({lat}, {lon}), nemocnice: {best_hospital} ({min_dist:.1f} km) +++")

                processed_count += 1

                # Uložíme cache každých 10 obcí
                if processed_count % 10 == 0 and new_cache_rows:
                    df_cache = pd.concat(
                        [df_cache, pd.DataFrame(new_cache_rows)], ignore_index=True)
                    save_cache(df_cache)
                    print(
                        f"--- Cache průběžně uložena ({processed_count} obcí zpracováno, {len(new_cache_rows)} nových) -> {CACHE_PATH} ---")

                    # Současně uložíme i cities_hospital_distances.csv
                    df_pro_vypocet.to_csv(
                        vystupni_soubor, index=False, encoding='utf-8-sig')
                    print(f"--- Průběžně uloženo i do {vystupni_soubor} ---")

                    new_cache_rows = []  # Vyčistíme buffer
            else:
                print(
                    f"--- Varování: Nepodařilo se geokódovat '{name}'. Zůstává bez souřadnic. ---")

        # Ulož cache (přidáme zbývající řádky, které nebyly uloženy)
        if new_cache_rows:
            df_cache = pd.concat(
                [df_cache, pd.DataFrame(new_cache_rows)], ignore_index=True)
            save_cache(df_cache)
            print(
                f"--- Cache finálně aktualizována ({len(new_cache_rows)} zbývajících záznamů) -> {CACHE_PATH} ---")

            # Uložíme i zbývající data do cities_hospital_distances.csv
            df_pro_vypocet.to_csv(
                vystupni_soubor, index=False, encoding='utf-8-sig')
            print(f"--- Zbývající data uložena i do {vystupni_soubor} ---")

    # Pokud ani po geokódování pořád chybí souřadnice, necháme je být (řádky později odfiltrujeme)
    df_pro_vypocet = df_pro_vypocet.dropna(subset=['Lat', 'Lon'])

# -------------------- Výpočet nejbližší nemocnice --------------------
vystupni_soubor = '../data/cities_hospital_distances.csv'

if df_pro_vypocet.empty or 'Lat' not in df_pro_vypocet.columns or 'Lon' not in df_pro_vypocet.columns:
    print("CHYBA: Nejsou dostupná žádná data se souřadnicemi pro výpočet.")
else:
    # Přidáme sloupce pro nemocnice, pokud ještě neexistují
    if 'Nejblizsi_nemocnice' not in df_pro_vypocet.columns:
        df_pro_vypocet['Nejblizsi_nemocnice'] = None
    if 'Vzdalenost_km' not in df_pro_vypocet.columns:
        df_pro_vypocet['Vzdalenost_km'] = None

    print("--- Zahajuji výpočet nejbližších nemocnic ---")
    processed_hospitals = 0

    for idx, obec in df_pro_vypocet.iterrows():
        obec_lat, obec_lon = obec['Lat'], obec['Lon']
        min_dist, best_name = np.inf, None

        for _, nem in df_nemocnice.iterrows():
            dist = haversine_distance(
                obec_lat, obec_lon, nem['Lat'], nem['Lon'])
            if dist < min_dist:
                min_dist = dist
                best_name = nem['Nazev_nemocnice']

        df_pro_vypocet.at[idx, 'Nejblizsi_nemocnice'] = best_name
        df_pro_vypocet.at[idx, 'Vzdalenost_km'] = min_dist

        processed_hospitals += 1

        # Průběžné ukládání každých 10 obcí
        if processed_hospitals % 10 == 0:
            df_pro_vypocet.to_csv(
                vystupni_soubor, index=False, encoding='utf-8-sig')
            print(
                f"--- Průběžně uloženo {processed_hospitals}/{len(df_pro_vypocet)} obcí -> {vystupni_soubor} ---")

    # Finální uložení
    df_pro_vypocet.to_csv(vystupni_soubor, index=False, encoding='utf-8-sig')
    print(f"\n--- FINÁLNÍ VÝSLEDKY ---")
    print(f"✓ Zpracováno {processed_hospitals} obcí")
    print(f"✓ Výsledky uloženy do: {vystupni_soubor}")
    print(f"\nUkázka prvních 5 řádků:")
    print(
        df_pro_vypocet[['Nazev_obce', 'Nejblizsi_nemocnice', 'Vzdalenost_km']].head())
