# The Impact of Economic-Geographical Factors on Healthcare Accessibility

This project analyzes healthcare accessibility across the Czech Republic, focusing on hospital distribution, capacity, and socioeconomic factors affecting healthcare access.

## Project Overview

This repository contains data analysis and statistical models examining various aspects of healthcare accessibility in the Czech Republic, including:

- **Geographic distribution** of hospitals and their accessibility from different municipalities
- **Economic factors** influencing hospital capacity and distribution
- **Demographic analysis** of hospitalization patterns
- **Distance-based accessibility** metrics for healthcare facilities

## Structure

- **data/** - Dataset files including hospital locations, municipality data, bed capacity, income statistics, and geographic information
- **honza_aleks/** - Economic and geographic clustering analysis, hospitalization patterns by age, income-capacity relationships
- **prokop_honza/** - Hospital accessibility analysis, distance calculations, and financial factors
- **sad/** - Demographic and family structure analysis
- **results/** - Output files and generated results

## Key Analyses

### Healthcare Capacity and Economics
- Population assignment to hospitals based on proximity
- Economic regions and their impact on hospital accessibility ([economic_geographic_clustering.ipynb](honza_aleks/economic_geographic_clustering.ipynb))
- Relationship between municipal income levels and hospital capacity ([income_capacity.ipynb](honza_aleks/income_capacity.ipynb))

### Accessibility Studies
- Distance-based hospital accessibility analysis ([main_accessibility.ipynb](prokop_honza/main_accessibility.ipynb))
- Impact of financial factors on distance to healthcare facilities ([distance_to_hospital_financial_factors.ipynb](prokop_honza/distance_to_hospital_financial_factors.ipynb))
- Hospital removal impact scenarios ([hospital_removal.ipynb](prokop_honza/hospital_removal.ipynb))

### Demographic Analysis
- Hospitalization rates by age distribution ([hospitalizations_age.ipynb](honza_aleks/hospitalizations_age.ipynb))
- Family structure and healthcare utilization ([family.ipynb](sad/family.ipynb))

## Data Sources

The analysis uses multiple datasets including:
- Hospital bed capacity data (`luzkovy_fond.csv`, `nasml_luzkovy_fond_2023.csv`)
- Municipality geographic and demographic information (`cities_geocache.csv`, `cities_with_all_data.csv`)
- Hospital locations in GeoJSON format (`mapanemocnic-mapa-nemocnic-v-cr.geojson`)
- Income statistics by municipality (`cities_geocache_with_prijmy.csv`)
- Age distribution data (`vek_obec_kod.csv`)

## Requirements

The project uses Python with standard data science libraries:
- pandas
- numpy
- matplotlib
- scikit-learn
- geopandas (for geographic data)

## Usage

Each analysis is contained in its own Jupyter notebook. Navigate to the respective directory and open the notebook files to view the analysis and results.

## Authors

- Aleksandra Bajićová
- Jan Hlavsa
- Prokop Jansa
- Jan Sadílek

## Citation

If you use this work in your research, please cite:

```
Bajićová, A., Hlavsa, J., Jansa, P., & Sadílek, J. (2025). 
The Impact of Economic-Geographical Factors on Healthcare Accessibility. 
GitHub repository: https://github.com/[your-username]/[repository-name]
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
