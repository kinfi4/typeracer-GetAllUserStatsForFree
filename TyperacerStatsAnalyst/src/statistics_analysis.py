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
        speeds = self.user_stats['speed'][::-1]
        means = [sum(speeds[:i]) / i for i in range(1, len(speeds) + 1)]

        plt.plot(self.user_stats['race'][::-1], means)
        plt.xlabel('Race')
        plt.ylabel('WPM')
        plt.legend(['Mean WPM'])
        plt.grid()
        plt.show()

    def append(self, data):
        self.user_stats.append(data)

    def __str__(self):
        return f'Stats: {self.user_stats[0]}'
