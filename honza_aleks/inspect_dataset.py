import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# --- 1. DATA LOADING AND PREPARATION ---
print("--- LOADING AND PREPARING DATA ---")
df = pd.read_csv('data/cities_with_all_data.csv')

# Convert 'Index_stari' to numeric, handling potential non-numeric errors
df['Index_stari'] = pd.to_numeric(df['Index_stari'], errors='coerce')

# Drop rows where essential data is missing
df = df.dropna(subset=['Index_stari', 'DPH', 'Total', 'Kraj'])

print(f"Original dataset size: {len(df)} rows")

# --- 2. ROBUST DATA FILTERING (QUANTILES) ---
df_robust = df.copy()

# remove outliers in every numeric column based on 1st and 99th percentiles
numeric_cols = df_robust.select_dtypes(include=[np.number]).columns.tolist()
for col in numeric_cols:
    low = df_robust[col].quantile(0.01)
    high = df_robust[col].quantile(0.99)
    df_robust = df_robust[(df_robust[col] >= low) & (df_robust[col] <= high)]

print(f"Robust dataset size (filtered 1st-99th percentile): {len(df_robust)} rows")
print("-" * 50)

# --- 3. CORRELATION ANALYSIS (The Justification for Dropping Predictors) ---
# "Also big correlation in economic factors... justify dropping predictors"

# Select economic indicators and demographic target
# corr cols should be all numeric variables
corr_cols = ['DPH', 'DNV', 'DPPO', 'DPFO', 'DPFO_srazkou', 'DPFO_zavisla_c', 'DPFO_zavisla_h',
            'Total', 'Men', 'Women', 'avg_age', 'avg_age_Men', 'avg_age_Women', 'Lat_y', 'Lon_y',
            'Vzdalenost_km', 'age_0_14_total', 'age_0_14_men', 'age_0_14_women', 'age_15_64_total',
            'age_15_64_men', 'age_15_64_women', 'age_65_plus_total', 'age_65_plus_men', 'age_65_plus_women',
            'Index_stari']
corr_matrix = df_robust[corr_cols].corr()

corr_matrix = corr_matrix.rename(columns={
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

corr_matrix = corr_matrix.rename(index={
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

# Plotting Heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5, vmin=-1, vmax=1, annot_kws={"size": 6})
plt.title('Correlation Matrix of all Numeric Variables (Excluded Outlier Cities)')
plt.tight_layout()
plt.savefig('eda_correlation_heatmap.pdf')
plt.show()
plt.close()
print("Saved: eda_correlation_heatmap.pdf")
print("-> Use this graph to justify removing collinear variables (e.g., VAT vs Corporate Income Tax).")

# --- 6. GEOSPATIAL MAP ---
# Checking spatial clustering of the variables

plt.figure(figsize=(14, 8))
scatter = plt.scatter(
    df_robust['Lon_x'], 
    df_robust['Lat_x'], 
    c=df_robust['Index_stari'], 
    cmap='RdYlBu_r', # Red = Older, Blue = Younger
    s=15, 
    alpha=0.7
)
plt.colorbar(scatter, label='Ageing Index')
plt.title('Geospatial Distribution of Ageing Index (Excluded Outlier Cities)')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.axis('equal')
plt.tight_layout()
plt.savefig('eda_ageing_map.pdf')
plt.show()
plt.close()
print("Saved: eda_ageing_map.pdf")

print("\n--- ALL TASKS COMPLETED ---")