from datetime import date
from typing import Optional

from src.parser import Parser
from src.statistics_analysis import StatisticsVisualizer


def parse(
    username: str,
    output_file: str,
    show_plots: bool = True,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> None:
    parser = Parser(start_date, end_date)
    stats = parser.parse_user_stats(username)
    stats.save_to_file(output_file)

    if show_plots:
        stats.plot_everything()


def plot_stats_from_file(filepath: str, start_date: Optional[date] = None, end_date: Optional[date] = None):
    stats = StatisticsVisualizer.get_stats_from_csv(filepath, start_date, end_date)

    stats.plot_everything()
