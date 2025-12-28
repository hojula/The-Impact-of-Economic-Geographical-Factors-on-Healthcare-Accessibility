import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Cell 1 ---
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.metrics import mean_squared_error, mean_absolute_error
import sys
import os
import warnings
warnings.filterwarnings('ignore')

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
from honza_aleks.lin_reg_utils import perform_all_tests

# --- Cell 3 ---
df = pd.read_csv(os.path.join(os.path.dirname(__file__), '../data/cities_with_all_data.csv'))

# Konverze na numerické hodnoty
cols = ['age_0_14_total', 'Total', 'Vzdalenost_km', 'DPFO_zavisla_h']
for col in cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna(subset=cols)

# Výpočet cílové proměnné
df['fraction_kids'] = df['age_0_14_total'] / 100

print(f"Celkem obcí: {len(df)}")
df[['fraction_kids', 'Vzdalenost_km', 'DPFO_zavisla_h', 'Total']].describe()

# --- Cell 5 ---
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].hist(df['fraction_kids'], bins=50, edgecolor='black', alpha=0.7)
axes[0].set_xlabel('Podíl dětí (0-14)')
axes[0].set_ylabel('Počet obcí')
axes[0].set_title('Distribuce podílu dětí')
axes[0].axvline(df['fraction_kids'].median(), color='red', linestyle='--', label=f'Medián: {df["fraction_kids"].median():.3f}')
axes[0].legend()

# Boxplot
axes[1].boxplot(df['fraction_kids'])
axes[1].set_ylabel('Podíl dětí')
axes[1].set_title('Boxplot - viditelné outliers')

plt.tight_layout()
plt.show()

print(f"\nPozorování: Většina obcí má podíl dětí kolem 3-10%, ale existují extrémní hodnoty.")
print(f"Minimum: {df['fraction_kids'].min():.4f} ({df['fraction_kids'].min()*100:.2f}%)")
print(f"Maximum: {df['fraction_kids'].max():.4f} ({df['fraction_kids'].max()*100:.2f}%)")

# --- Cell 7 ---
# Kopie pro analýzu
model_df = df.copy()

print(f"Před filtrací: {len(model_df)} obcí")

# # 1. Filtrovat realistický podíl dětí
# model_df = model_df[(model_df['fraction_kids'] >= 0.05) & (model_df['fraction_kids'] <= 0.25)]
# print(f"Po filtraci fraction_kids (5-25%): {len(model_df)} obcí")

# 2. Odstranit extrémní příjmy
q_low = model_df['DPFO_zavisla_h'].quantile(0.01)
q_high = model_df['DPFO_zavisla_h'].quantile(0.99)
model_df = model_df[(model_df['DPFO_zavisla_h'] >= q_low) & (model_df['DPFO_zavisla_h'] <= q_high)]
print(f"Po filtraci DPFO (1-99%): {len(model_df)} obcí")

# Finální datová sada
model_data = model_df[['fraction_kids', 'Vzdalenost_km', 'DPFO_zavisla_h', 'Total']].dropna()
print(f"\nFinální dataset: {len(model_data)} obcí")
model_data.describe()

# --- Cell 9 ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 1. Vzdálenost vs podíl dětí
axes[0].scatter(model_data['Vzdalenost_km'], model_data['fraction_kids'], alpha=0.3, s=10)
z = np.polyfit(model_data['Vzdalenost_km'], model_data['fraction_kids'], 1)
p = np.poly1d(z)
x_line = np.linspace(model_data['Vzdalenost_km'].min(), model_data['Vzdalenost_km'].max(), 100)
axes[0].plot(x_line, p(x_line), 'r-', linewidth=2, label=f'Trend')
axes[0].set_xlabel('Vzdálenost od nemocnice (km)')
axes[0].set_ylabel('Podíl dětí')
axes[0].set_title('Podíl dětí vs Vzdálenost')
axes[0].legend()

# 2. Příjmy vs podíl dětí
axes[1].scatter(model_data['DPFO_zavisla_h'], model_data['fraction_kids'], alpha=0.3, s=10)
z2 = np.polyfit(model_data['DPFO_zavisla_h'], model_data['fraction_kids'], 1)
p2 = np.poly1d(z2)
x_line2 = np.linspace(model_data['DPFO_zavisla_h'].min(), model_data['DPFO_zavisla_h'].max(), 100)
axes[1].plot(x_line2, p2(x_line2), 'r-', linewidth=2, label='Trend')
axes[1].set_xlabel('DPFO_zavisla_h (příjmy)')
axes[1].set_ylabel('Podíl dětí')
axes[1].set_title('Podíl dětí vs Příjmy domácností')
axes[1].legend()

plt.tight_layout()
plt.show()

print("\nPozorování:")
print("- Vzdálenost: Mírný POZITIVNÍ trend (více dětí dále od nemocnic)")
print("- Příjmy: NEGATIVNÍ trend (více dětí v obcích s nižšími příjmy)")

# --- Cell 11 ---
# Fitování modelu
formula = 'fraction_kids ~ Vzdalenost_km + DPFO_zavisla_h'
model = smf.wls(formula=formula, data=model_data, weights=model_data['Total']).fit()

print(model.summary())

# --- Cell 14 ---
# perform_all_tests(model, model_data, features=['Vzdalenost_km', 'DPFO_zavisla_h'], model_name='Family Model', y_col='fraction_kids')

# --- Cell 16 ---
# Výpočet metrik - musíme použít váhy (Total), protože model je WLS
y_true = model_data['fraction_kids']
y_pred = model.fittedvalues
weights = model_data['Total']

# Vážené metriky
rmse = np.sqrt(mean_squared_error(y_true, y_pred, sample_weight=weights))
mae = mean_absolute_error(y_true, y_pred, sample_weight=weights)

# Vážený baseline (vážený průměr)
weighted_mean = np.average(y_true, weights=weights)
baseline_rmse = np.sqrt(mean_squared_error(y_true, [weighted_mean]*len(y_true), sample_weight=weights))

print("=" * 50)
print("METRIKY MODELU (Vážené podle populace)")
print("=" * 50)
print(f"R² (Weighted):      {model.rsquared:.4f} ({model.rsquared*100:.1f}%)")
print(f"Adj R² (Weighted):  {model.rsquared_adj:.4f}")
print(f"RMSE (Weighted):    {rmse:.4f}")
print(f"MAE (Weighted):     {mae:.4f}")
print(f"Baseline RMSE (W):  {baseline_rmse:.4f}")
print("=" * 50)
print(f"\nModel vysvětluje {model.rsquared*100:.1f}% vážené variability.")
print(f"Zlepšení oproti (váženému) průměru: {((baseline_rmse-rmse)/baseline_rmse)*100:.1f}%")
