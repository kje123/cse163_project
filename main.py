import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns


def load_data(csv):
    df = pd.read_csv(csv)
    return df


def late_routes(df):
    grouped_6_20 = df.groupby('Rte')['# 6-20 Min Late'].mean()
    grouped_6_20 = grouped_6_20.nlargest(10).sort_values()
    grouped_6_20 = grouped_6_20[grouped_6_20 > 0]
    grouped_21_30 = df.groupby('Rte')['# 21-30 Min Late'].mean()
    grouped_21_30 = grouped_21_30.nlargest(10).sort_values()
    grouped_21_30 = grouped_21_30[grouped_21_30 > 0]

    fig, [ax1, ax2] = plt.subplots(2)
    grouped_6_20.plot.bar(ax=ax1)
    grouped_21_30.plot.bar(ax=ax2)
    ax1.tick_params('x', labelrotation=0)
    plt.savefig('number_late.png')


def main():
    df = load_data("data/AllRoutes-OTP-Details-2019-04.csv")
    late_routes(df)


if __name__ == "__main__":
    main()
