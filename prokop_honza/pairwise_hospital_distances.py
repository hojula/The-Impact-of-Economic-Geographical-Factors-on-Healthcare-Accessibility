import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Načtení dat
df = pd.read_csv('cities_with_all_data_druha_nemocnice.csv')

# Výběr relevantních sloupců
df_hospitals = df[['Nejblizsi_nemocnice',
                   'Druha_nejblizsi_nemocnice']].dropna()

# Vytvoření crosstab (contingency table)
confusion_matrix = pd.crosstab(
    df_hospitals['Druha_nejblizsi_nemocnice'],
    df_hospitals['Nejblizsi_nemocnice'],
    margins=False
)

# Vytvoření heatmapy
fig, ax = plt.subplots(figsize=(20, 16))

# Vytvoření heatmapy s čísly
sns.heatmap(confusion_matrix,
            annot=True,
            fmt='d',
            cmap='YlOrRd',
            cbar_kws={'label': 'Počet měst'},
            ax=ax,
            linewidths=0.5,
            linecolor='gray')

# Nastavení popisků
ax.set_xlabel('Nejbližší nemocnice', fontsize=14, fontweight='bold')
ax.set_ylabel('Druhá nejbližší nemocnice', fontsize=14, fontweight='bold')
ax.set_title('Confusion Matrix: Kombinace nejbližší a druhé nejbližší nemocnice pro každé město',
             fontsize=16, fontweight='bold', pad=20)

# Rotace popisků pro lepší čitelnost
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.yticks(rotation=0, fontsize=10)

plt.tight_layout()
plt.savefig('hospital_confusion_matrix.png', dpi=300, bbox_inches='tight')
plt.show()

# Výpis statistik
print("="*80)
print("CONFUSION MATRIX - Kombinace nemocnic")
print("="*80)
print(confusion_matrix)
print("\n" + "="*80)
print("ZÁKLADNÍ STATISTIKY")
print("="*80)
print(f"\nCelkový počet měst: {len(df_hospitals)}")
print(
    f"Počet různých nejbližších nemocnic: {df_hospitals['Nejblizsi_nemocnice'].nunique()}")
print(
    f"Počet různých druhých nejbližších nemocnic: {df_hospitals['Druha_nejblizsi_nemocnice'].nunique()}")

print("\n" + "-"*80)
print("TOP 10 kombinací (nejbližší → druhá nejbližší):")
print("-"*80)
combinations = df_hospitals.groupby(
    ['Nejblizsi_nemocnice', 'Druha_nejblizsi_nemocnice']).size()
combinations_sorted = combinations.sort_values(ascending=False).head(10)
for i, ((first, second), count) in enumerate(combinations_sorted.items(), 1):
    print(f"{i:2d}. {first:40s} → {second:40s} : {count:4d} měst")

print("\n" + "-"*80)
print("Nejčastější nejbližší nemocnice:")
print("-"*80)
top_closest = df_hospitals['Nejblizsi_nemocnice'].value_counts().head(10)
for i, (hospital, count) in enumerate(top_closest.items(), 1):
    print(f"{i:2d}. {hospital:50s} : {count:4d} měst")

print("\n" + "-"*80)
print("Nejčastější druhá nejbližší nemocnice:")
print("-"*80)
top_second = df_hospitals['Druha_nejblizsi_nemocnice'].value_counts().head(10)
for i, (hospital, count) in enumerate(top_second.items(), 1):
    print(f"{i:2d}. {hospital:50s} : {count:4d} měst")

print("\n" + "="*80)
print("ARGMAX - Nejčastější druhá nejbližší nemocnice pro každou nejbližší nemocnici")
print("="*80)
# Pro každý sloupec (nejbližší nemocnici) najdeme řádek s maximální hodnotou (nejčastější druhou nejbližší)
for col in confusion_matrix.columns:
    # pouze pokud existují města s touto nejbližší nemocnicí
    if confusion_matrix[col].sum() > 0:
        # argmax - název řádku s max hodnotou
        max_row = confusion_matrix[col].idxmax()
        max_value = confusion_matrix[col].max()  # max hodnota
        total = confusion_matrix[col].sum()  # celkový počet měst
        percentage = (max_value / total) * 100
        print(f"\n{col}")
        print(f"  → Nejčastější druhá: {max_row}")
        print(f"  → Počet měst: {max_value}/{total} ({percentage:.1f}%)")
