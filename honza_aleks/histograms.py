# load data cities_with_all_data.csv and create histograms for every numeric column
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math

def optimal_bins(series, max_bins=200):
    arr = series.dropna().values
    n = len(arr)
    if n <= 1:
        return 1
    data_min, data_max = arr.min(), arr.max()
    data_range = data_max - data_min
    if data_range == 0:
        return 1
    q75, q25 = np.percentile(arr, [75, 25])
    iqr = q75 - q25
    # Freedman–Diaconis rule
    if iqr > 0:
        bin_width = 2 * iqr * (n ** (-1/3))
        if bin_width > 0:
            bins = int(np.ceil(data_range / bin_width))
        else:
            bins = int(np.ceil(np.log2(n) + 1))  # Sturges fallback
    else:
        bins = int(np.ceil(np.log2(n) + 1))  # Sturges fallback for low-variability data
    bins = max(1, min(bins, max_bins))
    return bins

data = pd.read_csv('data/cities_with_all_data.csv')

# rename numeric columns for better readability
data = data.rename(columns={
    'DPH': 'VAT',
    'DNV': 'Property Tax',
    'DPPO': 'Corporate Income Tax',
    'DPFO': 'Personal Income Tax',
    'DPFO_srazkou': 'Personal Income Tax Withholding',
    'DPFO_zavisla_c': 'Personal Income Tax Dependent Count',
    'DPFO_zavisla_h': 'Personal Income Tax Dependent Amount',
    'Total': 'Total population',
    'Men': 'Men',
    'Women': 'Women',
    'avg_age': 'Average Age',
    'avg_age_Men': 'Average Age of Men',
    'avg_age_Women': 'Average Age of Women',
    'Lat_y': 'Latitude',
    'Lon_y': 'Longitude',
    'Vzdalenost_km': 'Distance to the nearest hospital (km)',
    'age_0_14_total': 'Percentage of Age 0-14 Total',
    'age_0_14_men': 'Percentage of Age 0-14 Men',
    'age_0_14_women': 'Percentage of Age 0-14 Women',
    'age_15_64_total': 'Percentage of Age 15-64 Total',
    'age_15_64_men': 'Percentage of Age 15-64 Men',
    'age_15_64_women': 'Percentage of Age 15-64 Women',
    'age_65_plus_total': 'Percentage of Age 65 Plus Total',
    'age_65_plus_men': 'Percentage of Age 65 Plus Men',
    'age_65_plus_women': 'Percentage of Age 65 Plus Women',
    'Index_stari': 'Age Index',
})

# select concrete numeric columns
numeric_columns = data.select_dtypes(include=['number']).columns
numeric_columns = numeric_columns.drop(['Cislo_obce', 'Lat_x', 'Lon_x', 'Prumerny_vek_celkem' , 'Prumerny_vek_muzi', 'Prumerny_vek_zeny', 'key'])  # drop non-relevant numeric columns
# print relevant numeric columns
print("Relevant numeric columns for histogram:")
print(numeric_columns)

#remove outlies from numeric columns with quantile method
for column in numeric_columns:
    low = data[column].quantile(0.01)
    high = data[column].quantile(0.99)
    data = data[(data[column] >= low) & (data[column] <= high)]

# n of histograms
n = len(numeric_columns)
print(n)

# demographic columns
demographic_columns = [
    'Total population', 'Men', 'Women', 
    'Average Age', 'Average Age of Men', 'Average Age of Women',
    'Percentage of Age 0-14 Total', 'Percentage of Age 0-14 Men', 'Percentage of Age 0-14 Women',
    'Percentage of Age 15-64 Total', 
    'Percentage of Age 15-64 Men', 'Percentage of Age 15-64 Women', 
    'Percentage of Age 65 Plus Total', 'Percentage of Age 65 Plus Men',
    'Percentage of Age 65 Plus Women', 'Age Index'
]

for i in range(0, len(demographic_columns), 4):
    
    # Změna: mřížka 2x2 (místo 4x2) a upravená velikost obrázku
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f'Demographic Data Distributions', fontsize=16)
    
    # Vybereme aktuální čtveřici sloupců
    batch_columns = demographic_columns[i:i+4]
    
    for j, column in enumerate(batch_columns):
        # Indexování do mřížky 2x2 (j//2 je řádek 0 nebo 1, j%2 je sloupec 0 nebo 1)
        ax = axes[j//2, j%2]
        
        # BEZPEČNÉ NAČTENÍ DAT (Oprava chyby TypeError a IndexError)
        # 1. Bereme data z hlavního DataFrame 'data'
        # 2. Vynutíme převod na čísla (errors='coerce' udělá z textu NaN)
        series_clean = pd.to_numeric(data[column], errors='coerce').dropna()
        
        # Kontrola, jestli zbylo dost dat
        if len(series_clean) <= 1:
            ax.text(0.5, 0.5, 'Not enough data', ha='center', va='center')
            ax.set_title(column)
            continue

        # Výpočet binů a vykreslení
        bins = optimal_bins(series_clean)
        ax.hist(series_clean, bins=bins, color='skyblue', edgecolor='black')
        
        ax.set_title(column)
        ax.set_xlabel(column)
        ax.set_ylabel('Number of Cities')
        
    # Pokud by v poslední várce bylo méně než 4 grafy, skryjeme prázdná okna
    for k in range(len(batch_columns), 4):
        axes[k//2, k%2].axis('off')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(f'histograms_demographic_batch_{i//4 + 1}.pdf')
    plt.show()


economic_columns = ['VAT', 'Property Tax', 'Corporate Income Tax', 'Personal Income Tax',
                    'Personal Income Tax Withholding', 'Personal Income Tax Dependent Count',
                    'Personal Income Tax Dependent Amount']


economic_columns = ['VAT', 'Property Tax', 'Corporate Income Tax', 'Personal Income Tax',
                    'Personal Income Tax Withholding', 'Personal Income Tax Dependent Count',
                    'Personal Income Tax Dependent Amount']

# Nastavení: kolik grafů chceme na jeden obrázek (2x2 = 4)
plots_per_fig = 4
num_figures = math.ceil(len(economic_columns) / plots_per_fig)

for i in range(num_figures):
    # Vytvoření figure a os (axes) pro mřížku 2x2
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()  # Zploštění pole os pro snadnou iteraci (0, 1, 2, 3)
    
    # Výběr sloupců pro aktuální figure
    start_idx = i * plots_per_fig
    end_idx = start_idx + plots_per_fig
    current_columns = economic_columns[start_idx:end_idx]
    
    for j, column in enumerate(current_columns):
        ax = axes[j] # Vybereme konkrétní pod-graf
        
        # Čištění dat
        series_clean = pd.to_numeric(data[column], errors='coerce').dropna()
        
        # Kontrola dostatku dat
        if len(series_clean) <= 1:
            ax.text(0.5, 0.5, 'Not enough data', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(column)
            continue
            
        # Vykreslení histogramu
        # Pozor: voláme optimal_bins, předpokládám, že funkce existuje
        bins = optimal_bins(series_clean)
        ax.hist(series_clean, bins=bins, color='lightgreen', edgecolor='black')
        ax.set_title(f'Distribution of {column}')
        ax.set_xlabel(column)
        ax.set_ylabel('Number of Cities')

    # Odstranění prázdných os (pokud v mřížce zbylo místo, např. ve druhém okně)
    for k in range(len(current_columns), len(axes)):
        fig.delaxes(axes[k])

    plt.tight_layout()
    plt.savefig(f'histograms_economic_batch_{i+1}.pdf')
    plt.show()

# plot histogram for 'Distance to the nearest hospital (km)' column
plt.figure(figsize=(8, 6))
series_clean = pd.to_numeric(data['Distance to the nearest hospital (km)'], errors='coerce').dropna()
bins = optimal_bins(series_clean)
plt.hist(series_clean, bins=bins, color='salmon', edgecolor='black')
plt.title('Distribution of Distance to the Nearest Hospital (km)')
plt.xlabel('Distance to the Nearest Hospital (km)')
plt.ylabel('Number of Cities')
plt.tight_layout()
plt.savefig('histogram_distance_to_hospital.pdf')
plt.show()

# plot histogram for 'Latitude' and 'Longitude' columns
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
series_clean = pd.to_numeric(data['Latitude'], errors='coerce').dropna()
bins = optimal_bins(series_clean)
plt.hist(series_clean, bins=bins, color='violet', edgecolor='black')
plt.title('Distribution of Latitude')
plt.xlabel('Latitude')
plt.ylabel('Number of Cities')
plt.subplot(1, 2, 2)
series_clean = pd.to_numeric(data['Longitude'], errors='coerce').dropna()
bins = optimal_bins(series_clean)
plt.hist(series_clean, bins=bins, color='orange', edgecolor='black')
plt.title('Distribution of Longitude')
plt.xlabel('Longitude')
plt.ylabel('Number of Cities')
plt.tight_layout()
plt.savefig('histogram_latitude_longitude.pdf')
plt.show()


