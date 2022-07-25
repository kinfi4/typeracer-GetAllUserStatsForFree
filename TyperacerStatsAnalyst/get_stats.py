import argparse
from typing import Optional
from datetime import datetime, date

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


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-n', '--no-parsing', help='Dont parse user stats from typeracer, use info from file instead', action='store_true')
    arg_parser.add_argument('-u', '--username', help='Username of the account to parse info about')
    arg_parser.add_argument('-f', '--filename', help='Filepath where to store the parsed info, OR file where script can gather info from, if --no-parsing specified')
    arg_parser.add_argument('--start-date', help='Date in format: %d-%m-%Y, fetched results will start from that date (inclusive). Example: --start-date "24-07-2022"')
    arg_parser.add_argument('--end-date', help='Date in format: %d-%m-%Y, fetched results will be before specified date (exclusive). Example: --start-date "24-07-2022"')
    arg_parser.add_argument('--hide-plots', help='Dont show any plots', action='store_true')

    args = arg_parser.parse_args()

    start_date_arg = datetime.strptime(args.start_date, '%d-%m-%Y').date() if args.start_date else None
    end_date_arg = datetime.strptime(args.end_date, '%d-%m-%Y').date() if args.end_date else None

    if start_date_arg and end_date_arg and start_date_arg > end_date_arg:
        print('Start date is later than end date.')
        exit(code=1)

    if args.no_parsing:
        if not args.filename:
            print('You have to specify the filepath from which I have to get statistics')
            exit(code=1)

        plot_stats_from_file(args.filename, start_date_arg, end_date_arg)
    else:
        if not args.username:
            print('You have to specify the username of the account you wanna parse info about')
            exit(code=1)

        filename = args.filename if args.filename else f'{args.username}-stats.csv'

        parse(
            username=args.username,
            output_file=filename,
            show_plots=not args.hide_plots,
            start_date=start_date_arg,
            end_date=end_date_arg
        )
