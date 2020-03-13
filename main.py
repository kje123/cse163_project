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
    df2_filtered = df2[['OBJECTID', 'X', 'Y', 'ROUTE_LIST']]
    # 'explodes' list into multiple new rows with values
    # (thanks @YOBEN_S on stackexchange! :)
    df2_expld = df2.set_index('OBJECTID').ROUTE_LIST.apply(pd.Series).stack()\
        .reset_index(level=0).rename(columns={0: 'ROUTE'})
    df2_merged = df2_filtered.merge(df2_expld, on='OBJECTID')
    merged = df.merge(df2_merged, left_on='Rte', right_on='ROUTE', how='inner')
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


def plot_county(shape, ax1, ax2):
    test = gpd.read_file(shape)
    test.plot(facecolor='none', edgecolor='black', ax=ax1)
    test.plot(facecolor='none', edgecolor='black', ax=ax2)


def stop_map(df):
    fig, [ax1, ax2] = plt.subplots(1, 2, figsize=(10, 6))
    plot_county('data/king_county_shape/Regional_Transit_District__rtadst_area.shp', ax1, ax2)

    grouped = df.groupby('Rte').agg({'# 6-20 Min Late': 'mean',
                                     '# 21-30 Min Late': 'mean',
                                     'X': 'first', 'Y': 'first'})
    gdf = gpd.GeoDataFrame(grouped,
                           geometry=gpd.points_from_xy
                           (pd.to_numeric(grouped['X']),
                            pd.to_numeric(grouped['Y'])))
    gdf.plot(marker='*', c=gdf['# 6-20 Min Late'],
             markersize=14, cmap='inferno', ax=ax1)
    gdf.plot(marker='*', c=gdf['# 21-30 Min Late'],
             markersize=14, cmap='inferno', ax=ax2)
    fig2, (ax3, ax4) = plt.subplots(1, 2)
    map1 = ax3.imshow(np.stack([gdf['# 6-20 Min Late'],
                                gdf['# 6-20 Min Late']]), cmap='inferno')
    map2 = ax4.imshow(np.stack([gdf['# 21-30 Min Late'],
                                gdf['# 21-30 Min Late']]), cmap='inferno')
    fig.colorbar(map1, ax=ax1)
    fig.colorbar(map2, ax=ax2)
    fig.suptitle('Average number of times busses are late, per bus stop',
                 fontsize='x-large')
    ax1.set_title('6-20 minutes')
    ax2.set_title('21-30 minutes')
    plt.tight_layout()
    fig.savefig('map.png')


def over_time(df):
    pass


def main():
    df = load_data('data/AllRoutes-OTP-Details-2019-04.csv',
                   'data/Transit_Stops_for_King_County_Metro__transitstop_point.csv')
    # late_routes(df)
    # inbound_outbound(df)
    stop_map(df)


if __name__ == '__main__':
    main()
