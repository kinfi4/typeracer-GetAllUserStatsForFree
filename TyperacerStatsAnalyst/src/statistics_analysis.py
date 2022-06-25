from datetime import date

import pandas as pd
import matplotlib.pyplot as plt


class StatisticsVisualizer:
    def __init__(self, user_stats_table: pd.DataFrame):
        self.user_stats_df = user_stats_table

    @classmethod
    def get_stats_from_csv(cls, filename: str):
        return cls(pd.read_csv(filename))

    def save_to_file(self, filepath: str):
        self.user_stats_df.to_csv(filepath, index=False)

    def plot_everything(self):
        self.plot_activity_by_date_distribution()
        self.plot_places()
        self.plot_speeds()
        self.plot_mean_wpm()
        self.plot_mean_tens()

        plt.show()

    def plot_mean_wpm(self):
        show_every_x_records = 10

        speeds = list(map(int, self.user_stats_df['speed'][::-1].values))
        means = [sum(speeds[:i]) / i for i in range(1, len(speeds) + 1) if i % show_every_x_records == 0]

        _ = plt.figure(1)
        plt.plot(list(filter(lambda idx: int(idx) % show_every_x_records == 0, self.user_stats_df['race'][::-1].values)), means)
        plt.xlabel('Race')
        plt.ylabel('WPM')
        plt.legend(['Mean WPM'])

    def plot_speeds(self):
        speeds = list(map(int, self.user_stats_df['speed'][::-1].values))
        max_speed, min_speed = max(speeds), min(speeds)

        _ = plt.figure(2)
        plt.scatter(self.user_stats_df['race'][::-1], speeds, s=0.3, c='red')
        plt.xlabel('Race')
        plt.ylabel('WPM')
        plt.legend(['Speed in WPM'])
        plt.ylim((min_speed - 30, max_speed + 30))

    def plot_mean_tens(self):
        show_every_x_records = 20

        speeds = list(map(int, self.user_stats_df['speed'][::-1].values))
        means_tens, race_indexes = [], []

        for idx in range(1, len(speeds) + 1):
            if idx < 11:
                race_indexes.append(idx)
                means_tens.append(sum(speeds[:idx]) / idx)
            elif idx % show_every_x_records == 0:
                race_indexes.append(idx)
                means_tens.append(sum(speeds[idx - 10:idx]) / 10)

        _ = plt.figure(3)
        plt.plot(race_indexes, means_tens)
        plt.xlabel('Race')
        plt.ylabel('WPM')
        plt.legend(['Mean speed for last 10 races'])

    def plot_places(self):
        places_took = self.user_stats_df[self.user_stats_df['place'].str.contains('/5')]
        places_took = places_took['place'].value_counts().sort_index(key=lambda x: x.str[0].astype(int))

        _ = plt.figure(4)
        plt.bar(places_took.index, places_took.values, color='green')
        plt.xlabel('Place took in race')
        plt.ylabel('Number of races')

    def plot_activity_by_date_distribution(self):
        df_dates_transformed = pd.to_datetime(self.user_stats_df['date'])
        df_dates_transformed = df_dates_transformed.dt.to_period('M')
        dates_with_races_number = df_dates_transformed.value_counts().sort_index()

        dates_with_races_number.index = pd.to_datetime(dates_with_races_number.index.to_timestamp())

        _ = plt.figure(5)
        plt.plot(dates_with_races_number.index, dates_with_races_number.values, color='green')
        plt.xlabel('Date')
        plt.ylabel('Number of races')

    def append(self, data):
        self.user_stats_df.append(data)

    def __str__(self):
        return f'Stats: {self.user_stats_df[0]}'
