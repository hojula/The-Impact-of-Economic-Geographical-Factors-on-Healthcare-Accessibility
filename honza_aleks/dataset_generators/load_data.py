import pandas as pd
import os
from typing import Tuple
import numpy as np
import matplotlib.pyplot as plt


if __name__ == '__main__':
    files = ["cities_geocache_with_prijmy.csv", "cities_hospital_distances.csv",
             "vek_obec_kod.csv", "nemocnice_kompletni.csv"]
    dfs = {}
    cities_with_all_data = None
    for file in files:
        path = os.path.join("../data", file)
        df = pd.read_csv(path)
        dfs[file] = df
        """
        print("Head of", file)
        print(df.head())
        print("\n")
        input("Press Enter to continue..."
        """
    # merge dataframes - left join
    cities_with_all_data = dfs["cities_geocache_with_prijmy.csv"]
    cities_with_all_data = cities_with_all_data.merge(
        dfs["cities_hospital_distances.csv"], on="Cislo_obce", how="left")
    cities_with_all_data = cities_with_all_data.merge(
        dfs["vek_obec_kod.csv"], on="Cislo_obce", how="left")

    # rename keys
    # _17 = 45.980903711672944, _18 = 43.88520130576714, _19 = 48.02978723404255
    cities_with_all_data = cities_with_all_data.rename(
        columns={"Total.1": "avg_age", "Men.1": "avg_age_Men", "Women.1": "avg_age_Women"})
    # 0-14_let_celkem', '0-14_let_muzi',
    # '0-14_let_zeny', '15-64_let_celkem', '15-64_let_muzi', '15-64_let_zeny',
    # '65+_let_celkem', '65+_let_muzi', '65+_let_zeny'
    cities_with_all_data = cities_with_all_data.rename(
        columns={"0-14_let_celkem": "age_0_14_total",
                 "0-14_let_muzi": "age_0_14_men",
                 "0-14_let_zeny": "age_0_14_women",
                 "15-64_let_celkem": "age_15_64_total",
                 "15-64_let_muzi": "age_15_64_men",
                 "15-64_let_zeny": "age_15_64_women",
                 "65+_let_celkem": "age_65_plus_total",
                 "65+_let_muzi": "age_65_plus_men",
                 "65+_let_zeny": "age_65_plus_women"
                 })

    # save merged dataframe
    output_path = os.path.join("../data", "cities_with_all_data.csv")
    cities_with_all_data.to_csv(output_path, index=False)
