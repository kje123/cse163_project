import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np


def load_data(csv, csv2):
    """
    takes in two csv files and returns them
    merged into one to use for analysis
    """
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
    """
    takes in a dataframe and plots the data of the top 10
    routes that reach stops both 6-20 minutes late and 21-30
    minutes late, on average (as a bar graph)

    saves said graph to the graphs folder
    """
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
    plt.savefig('graphs/number_late.png')


def inbound_outbound(df):
    """
    takes in a dataframe and plots the data of the average
    percent in which stops are both 6-20 minutes late and 21-30
    minutes late, seperated by whether the trip was an inbound
    (going into a main city), or outbound (going away from a main city)
    (as a double bar graph)

    saves said graph to the graphs folder
    """
    df['% 6-20 Min Late'] = df['% 6-20 Min Late'].str.strip('%').astype(float)
    df['% 21-30 Min Late'] = df['% 21-30 Min Late'].str.strip('%') \
        .astype(float)
    df_g = df.groupby('InOut')['% 6-20 Min Late', '% 21-30 Min Late'].mean()

    df_g.plot.bar()
    plt.xlabel('Type of trip')
    plt.xticks(np.arange(2), ('Inbound', 'Outbound'))
    plt.tick_params('x', labelrotation=0)
    plt.ylabel('% (Out of 100)')
    plt.savefig('graphs/outbound_inbound.png')


def plot_county(shape, ax1, ax2):
    """
    takes in a shapefile, and two axis and plots the shapefile on the axis
    """
    test = gpd.read_file(shape)
    test.plot(facecolor='none', edgecolor='black', ax=ax1)
    test.plot(facecolor='none', edgecolor='black', ax=ax2)


def stop_map(df):
    """
    takes in a dataframe and creates two maps which places a point
    on each bus stop and colors it depending, on average, how late
    busses tend to be to said stop, seperated by 6-20 minutes late
    and 21-30 minutes late

    saves said graph to the graphs folder
    """
    fig, [ax1, ax2] = plt.subplots(1, 2, figsize=(10, 6))
    shp = 'data/king_county_shape/Regional_Transit_District__rtadst_area.shp'
    plot_county(shp, ax1, ax2)

    grouped = df.groupby('Rte').agg({'# 6-20 Min Late': 'mean',
                                     '# 21-30 Min Late': 'mean',
                                     'X': 'first', 'Y': 'first'})
    gdf = gpd.GeoDataFrame(grouped,
                           geometry=gpd.points_from_xy
                           (pd.to_numeric(grouped['X']),
                            pd.to_numeric(grouped['Y'])))
    gdf.plot(marker='*', column=gdf['# 6-20 Min Late'],
             markersize=16, cmap='cool', ax=ax1)
    gdf.plot(marker='*', column=gdf['# 21-30 Min Late'],
             markersize=16, cmap='cool', ax=ax2)
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
    fig.savefig('graphs/map.png')


def over_time(df):
    """
    takes in a dataframe and creates a line plot representing
    how late busses are, on average, for each hour in the day,
    seperated by being late by 6-20 minutes late and 21-30
    minutes late

    saves said graph to the graphs folder
    """
    fig, [ax1, ax2] = plt.subplots(1, 2, figsize=(10, 8))
    df_hour = df
    df_hour['Hour'] = pd.to_datetime(df['Trip St Tm'],
                                     format='%I:%M %p').dt.hour
    grouped = df_hour.groupby('Hour').agg({'# 6-20 Min Late': 'mean',
                                           '# 21-30 Min Late': 'mean'})
    x_labels = ['12AM', '1AM', '2AM', '3AM', '4AM', '5AM', '6AM', '7AM',
                '8AM', '9AM', '10AM', '11AM', '12PM', '1PM', '2PM', '3PM',
                '4PM', '5PM', '6PM', '7PM', '8PM', '9PM', '10PM', '11PM']
    grouped.plot(y='# 6-20 Min Late', ax=ax1)
    grouped.plot(y='# 21-30 Min Late', ax=ax2)
    ax1.set_xticks(np.arange(24))
    ax1.set_xticklabels(x_labels)
    ax1.tick_params(labelrotation=90)
    ax2.set_xticks(np.arange(24))
    ax2.set_xticklabels(x_labels)
    ax2.tick_params(labelrotation=90)
    fig.suptitle('Average number of time busses are late, per hour of the day',
                 fontsize='x-large')
    fig.savefig('graphs/time_graph.png')


def main():
    df = load_data('data/AllRoutes-OTP-Details-2019-04.csv',
                   'data/transit_stops.csv')
    late_routes(df)
    inbound_outbound(df)
    stop_map(df)
    over_time(df)


if __name__ == '__main__':
    main()
