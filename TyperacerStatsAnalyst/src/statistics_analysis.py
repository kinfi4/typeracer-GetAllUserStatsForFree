from datetime import date
from typing import Optional

import pandas as pd
import matplotlib.pyplot as plt


class StatisticsVisualizer:
    def __init__(
        self,
        user_stats_table: pd.DataFrame,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> None:
        self._start_date = start_date
        self._end_date = end_date
        
        self.user_stats_df = self._filter_data_by_date(user_stats_table)

    @classmethod
    def get_stats_from_csv(cls, filename: str, start_date: date, end_date: date):
        return cls(pd.read_csv(filename), start_date, end_date)

    def save_to_file(self, filepath: str):
        self.user_stats_df.to_csv(filepath, index=False)

    def plot_everything(self):
        if self.user_stats_df.shape[0] == 0:
            print('Sorry but there are no data to parse')
            return

        self.plot_activity_by_date_distribution()
        self.plot_places()
        self.plot_speeds()
        self.plot_mean_wpm()
        self.plot_mean_tens()

        plt.show()

    def plot_mean_wpm(self):
        show_every_x_records = 10

        speeds = list(map(int, self.user_stats_df['speed'][::-1].values))
        means = [sum(speeds[i:i + 10]) / 10 for i in range(0, len(speeds), 10)]

        races_to_show = list(
            filter(
                lambda idx: int(idx) % show_every_x_records == 0,
                self.user_stats_df['race'][::-1].values
            )
        )

        truncated_to_same_size = list(zip(races_to_show, means))
        races_to_show, means = zip(*truncated_to_same_size)

        _ = plt.figure('Mean speed plot')
        plt.plot(races_to_show, means)
        plt.xlabel('Race')
        plt.ylabel('WPM')
        plt.legend(['Mean WPM'])

    def plot_speeds(self):
        speeds = list(map(int, self.user_stats_df['speed'][::-1].values))
        max_speed, min_speed = max(speeds), min(speeds)

        _ = plt.figure('Speeds plot')
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

        _ = plt.figure('Mean tens plot')
        plt.plot(race_indexes, means_tens)
        plt.xlabel('Race')
        plt.ylabel('WPM')
        plt.legend(['Mean speed for last 10 races'])

    def plot_places(self):
        places_took = self.user_stats_df[self.user_stats_df['place'].str.contains('/5')]
        places_took = places_took['place'].value_counts().sort_index(key=lambda x: x.str[0].astype(int))

        _ = plt.figure('Places took bar')
        plt.bar(places_took.index, places_took.values, color='green')
        plt.xlabel('Place took in race')
        plt.ylabel('Number of races')

    def plot_activity_by_date_distribution(self):
        df_dates_transformed = pd.to_datetime(self.user_stats_df['date'])
        first_date, last_date = df_dates_transformed.min(), df_dates_transformed.max()
        diff = last_date - first_date

        _ = plt.figure('Activity histogram')
        plt.hist(df_dates_transformed, bins=diff.days if diff.days else 1)
        plt.xlabel('Date')
        plt.ylabel('Number of races')

    def _filter_data_by_date(self, data: pd.DataFrame) -> pd.DataFrame:
        data['date'] = pd.to_datetime(data['date']).dt.date

        if self._start_date:
            data = data[data['date'] > self._start_date]

        if self._end_date:
            data = data[data['date'] <= self._end_date]

        return data
