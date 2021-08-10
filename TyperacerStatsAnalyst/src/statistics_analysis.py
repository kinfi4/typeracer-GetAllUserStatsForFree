import pandas as pd
import matplotlib.pyplot as plt


class Statistics:
    def __init__(self, user_stats_table: pd.DataFrame):
        self.user_stats = user_stats_table

    @classmethod
    def get_stats_from_csv(cls, filename):
        return cls(pd.read_csv(filename))

    def save_to_file(self, filepath):
        self.user_stats.to_csv(filepath, index=False)

    def plot_mean_wpm(self):
        speeds = list(map(int, self.user_stats['speed'][::-1].values))
        means = [sum(speeds[:i]) / i for i in range(1, len(speeds) + 1)]

        plot1 = plt.figure(1)
        plt.plot(self.user_stats['race'][::-1], means)
        plt.xlabel('Race')
        plt.ylabel('WPM')
        plt.legend(['Mean WPM'])

    def plot_speeds(self):
        speeds = list(map(int, self.user_stats['speed'][::-1].values))

        plot2 = plt.figure(2)
        plt.plot(self.user_stats['race'][::-1], speeds)
        plt.xlabel('Race')
        plt.ylabel('WPM')
        plt.legend(['Speed in WPM'])

    def append(self, data):
        self.user_stats.append(data)

    def __str__(self):
        return f'Stats: {self.user_stats[0]}'
