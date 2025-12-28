import pandas as pd
import numpy as np
from pathlib import Path

# -------------------- Haversine Distance --------------------
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # km
    lat1_rad, lon1_rad = np.radians(lat1), np.radians(lon1)
    lat2_rad, lon2_rad = np.radians(lat2), np.radians(lon2)
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = np.sin(dlat/2)**2 + np.cos(lat1_rad)*np.cos(lat2_rad)*np.sin(dlon/2)**2
    c = 2*np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R*c

# -------------------- Load Data --------------------
try:
    df_cities = pd.read_csv("data/cities_with_all_data.csv")
    print(f"✓ Loaded cities data: {len(df_cities)} rows")
except Exception as e:
    print(f"Error loading cities data: {e}")
    exit(1)

try:
    df_hospitals = pd.read_csv('data/nemocnice_kompletni.csv')
    print(f"✓ Loaded hospitals data: {len(df_hospitals)} rows")
except Exception as e:
    print(f"Error loading hospitals data: {e}")
    exit(1)

# -------------------- Prepare Data --------------------
# Use Lat_y, Lon_y from cities (geocoded coordinates)
df_cities = df_cities.dropna(subset=['Lat_y', 'Lon_y'])
df_hospitals = df_hospitals.dropna(subset=['Lat', 'Lon'])

print(f"After removing NaN coordinates: {len(df_cities)} cities, {len(df_hospitals)} hospitals")

# -------------------- Add Columns for Results --------------------
if 'Druha_nejblizsi_nemocnice' not in df_cities.columns:
    df_cities['Druha_nejblizsi_nemocnice'] = None
if 'Vzdalenost_druha_km' not in df_cities.columns:
    df_cities['Vzdalenost_druha_km'] = None

# -------------------- Compute Second Closest Hospital --------------------
print("\n--- Computing second closest hospitals ---")
processed = 0

for idx, obec in df_cities.iterrows():
    obec_lat = obec['Lat_y']
    obec_lon = obec['Lon_y']
    
    # Calculate distances to all hospitals
    distances = []
    for _, nem in df_hospitals.iterrows():
        dist = haversine_distance(
            obec_lat, obec_lon, nem['Lat'], nem['Lon'])
        distances.append((dist, nem['Nazev']))
    
    # Sort by distance
    distances.sort(key=lambda x: x[0])
    
    # Assign second closest
    if len(distances) > 1:
        df_cities.at[idx, 'Druha_nejblizsi_nemocnice'] = distances[1][1]
        df_cities.at[idx, 'Vzdalenost_druha_km'] = distances[1][0]

    processed += 1
    
    # Progress update every 100 cities
    if processed % 100 == 0:
        print(f"  Processed {processed}/{len(df_cities)} cities...")

# -------------------- Save Results --------------------
output_file = 'prokop_honza/cities_with_all_data_druha_nemocnice.csv'
df_cities.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"\n--- RESULTS ---")
print(f"✓ Processed {processed} cities")
print(f"✓ Results saved to: {output_file}")
print(f"\nSample (first 5 rows with second hospital):")
print(df_cities[['Nazev_obce', 'Nejblizsi_nemocnice', 'Vzdalenost_km', 
                  'Druha_nejblizsi_nemocnice', 'Vzdalenost_druha_km']].head())
