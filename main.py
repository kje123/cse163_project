import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np


def load_data(csv, csv2):
    df = pd.read_csv(csv)
    df['Rte'] = df['Rte'].astype(str)
    df2 = gpd.read_file(csv2)
    df2['ROUTE_LIST'].replace('', np.nan).dropna()
    # turn ROUTE_LIST column into an actual list object
    df2['ROUTE_LIST'] = df2['ROUTE_LIST'].str.split(' ')
    df2 = df2[['OBJECTID', 'X', 'Y', 'ROUTE_LIST']]
    # 'explodes' list into multiple new rows with values
    # (thanks @YOBEN_S on stackexchange! :)
    df2 = df2.set_index('OBJECTID').ROUTE_LIST.apply(pd.Series).stack()\
        .reset_index(level=0).rename(columns={0: 'ROUTE_LIST'})
    merged = df.merge(df2, left_on='Rte', right_on='ROUTE_LIST', how='inner')
    return merged


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
    ax2.tick_params('x', labelrotation=0)
    ax1.set_title(
        'Average # of stops for each route 6-20 Minutes late (top 10)')
    ax1.set_xlabel('Route Number')
    ax1.set_ylabel('# of Stops')
    ax2.set_title(
        'Average # of stops for each route 21-30 Minutes late (top 10)')
    ax2.set_xlabel('Route Number')
    ax2.set_ylabel('# of Stops')
    plt.tight_layout()
    plt.savefig('number_late.png')


def inbound_outbound(df):
    df['% 6-20 Min Late'] = df['% 6-20 Min Late'].str.strip('%').astype(float)
    df['% 21-30 Min Late'] = df['% 21-30 Min Late'].str.strip('%') \
        .astype(float)
    df_g = df.groupby('InOut')['% 6-20 Min Late', '% 21-30 Min Late'].mean()

    df_g.plot.bar()
    plt.xlabel('Type of trip')
    plt.xticks(np.arange(2), ('Inbound', 'Outbound'))
    plt.tick_params('x', labelrotation=0)
    plt.ylabel('% (Out of 100)')
    plt.savefig('outbound_inbound.png')


def stop_map(df):
    pass


def main():
    df = load_data('data/AllRoutes-OTP-Details-2019-04.csv',
                   'data/Transit_Stops_for_King_County_Metro__transitstop_point.csv')
    late_routes(df)
    inbound_outbound(df)


if __name__ == '__main__':
    main()
