import pandas as pd


class Statistics:
    def __init__(self, user_stats_table: pd.DataFrame):
        self.user_stats = user_stats_table

    @classmethod
    def get_stats_from_csv(cls, filename):
        return cls(pd.read_csv(filename))

    def save_to_file(self, filepath):
        self.user_stats.to_csv(filepath, index=False)

    def plot_mean_wpm(self):
        self.user_stats.plot('race', 'speed')

    def append(self, data):
        self.user_stats.append(data)

    def __str__(self):
        return f'Stats: {self.user_stats[0]}'
