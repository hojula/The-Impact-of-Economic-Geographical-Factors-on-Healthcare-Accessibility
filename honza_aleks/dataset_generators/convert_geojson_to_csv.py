import json
import pandas as pd
from pathlib import Path

# Cesta k GeoJSON souboru
geojson_path = '../data/mapanemocnic-mapa-nemocnic-v-cr.geojson'
output_csv = '../data/nemocnice_kompletni.csv'

print(f"Načítám GeoJSON ze souboru: {geojson_path}")

try:
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    hospitals = []

    for feature in geojson_data.get('features', []):
        props = feature.get('properties', {})
        geom = feature.get('geometry', {})
        coords = geom.get('coordinates', [])

        if len(coords) >= 2:
            # Základní informace
            hospital = {
                'Nazev': props.get('title', '').split(',')[0].strip(),
                'Adresa_plna': props.get('title', ''),
                'Popis': props.get('description', ''),
                'Lon': coords[0],
                'Lat': coords[1],
                'Group_ID': props.get('group', ''),
                'Marker_Color': props.get('marker-color', ''),
                'Marker_Symbol': props.get('marker-symbol', ''),
                'URL': props.get('url', ''),
                'Feature_ID': feature.get('id', '')
            }

            # Parsování popisu pro získání detailních informací
            description = props.get('description', '')

            # Extrakce zřizovatele
            if 'Zřizovatel:' in description:
                zrizovatel = description.split('Zřizovatel:')[
                    1].split('\n')[0].strip()
                hospital['Zrizovatel'] = zrizovatel
            else:
                hospital['Zrizovatel'] = ''

            # Extrakce počtu lůžek
            if 'Počet lůžek:' in description:
                luzka = description.split('Počet lůžek:')[
                    1].split('\n')[0].strip()
                hospital['Pocet_luzek'] = luzka
            else:
                hospital['Pocet_luzek'] = ''

            # Extrakce počtu lékařů
            if 'Počet lékařů:' in description:
                lekari = description.split('Počet lékařů:')[
                    1].split('\n')[0].strip()
                hospital['Pocet_lekaru'] = lekari
            else:
                hospital['Pocet_lekaru'] = ''

            # Extrakce počtu sester
            if 'Počet sester:' in description:
                sestry = description.split('Počet sester:')[
                    1].split('\n')[0].strip()
                hospital['Pocet_sester'] = sestry
            else:
                hospital['Pocet_sester'] = ''

            # Extrakce počtu hospitalizací
            if 'Počet hospitalizací:' in description:
                hospitalizace = description.split('Počet hospitalizací:')[
                    1].split('\n')[0].strip()
                hospital['Pocet_hospitalizaci'] = hospitalizace
            else:
                hospital['Pocet_hospitalizaci'] = ''

            # Extrakce počtu ambulantních vyšetření
            if 'Počet ambulantních vyšetření:' in description:
                ambulance = description.split('Počet ambulantních vyšetření:')[
                    1].split('\n')[0].strip()
                hospital['Pocet_ambulantnich_vysetreni'] = ambulance
            else:
                hospital['Pocet_ambulantnich_vysetreni'] = ''

            hospitals.append(hospital)

    # Vytvoření DataFrame
    df = pd.DataFrame(hospitals)

    # Seřazení podle názvu
    df = df.sort_values('Nazev')

    # Uložení do CSV
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')

    print(f"\n✓ Úspěšně převedeno {len(df)} nemocnic")
    print(f"✓ Soubor uložen: {output_csv}")
    print(f"\nSloupce v CSV:")
    for col in df.columns:
        print(f"  - {col}")

    print(f"\nPrvních 5 nemocnic:")
    print(df[['Nazev', 'Lat', 'Lon', 'Pocet_luzek', 'Zrizovatel']].head())

    print(f"\nStatistiky:")
    print(f"  - Celkem nemocnic: {len(df)}")
    print(
        f"  - S vyplněným počtem lůžek: {df['Pocet_luzek'].astype(str).apply(lambda x: x not in ['', '/', 'nan']).sum()}")
    print(
        f"  - S vyplněným URL: {df['URL'].astype(str).apply(lambda x: x not in ['', 'nan']).sum()}")

except FileNotFoundError:
    print(f"CHYBA: Soubor {geojson_path} nebyl nalezen!")
except json.JSONDecodeError:
    print(f"CHYBA: Soubor {geojson_path} není platný JSON!")
except Exception as e:
    print(f"CHYBA: {e}")
