import argparse

from src.parser import Parser
from src.statistics_analysis import StatisticsVisualizer


def parse(username, output_file, show_plots=True):
    parser = Parser()
    stats = parser.parse_user_stats(username)
    stats.save_to_file(output_file)

    if show_plots:
        stats.plot_everything()


def plot_stats_from_file(filepath: str):
    stats = StatisticsVisualizer.get_stats_from_csv(filepath)

    stats.plot_everything()


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-n', '--no-parsing', help='Dont parse user stats from typeracer, use info from file instead', action='store_true')
    arg_parser.add_argument('-u', '--username', help='Username of the account to parse info about')
    arg_parser.add_argument('-f', '--filename', help='Filepath where to store the parsed info, OR file where script can gather info from, if --no-parsing specified')
    arg_parser.add_argument('--hide-plots', help='Dont show any plots', action='store_true')

    args = arg_parser.parse_args()

    if args.no_parsing:
        if not args.filename:
            print('You have to specify the filepath from which I have to get statistics')
            exit(code=1)

        plot_stats_from_file(args.filename)
    else:
        if not args.username:
            print('You have to specify the username of the account you wanna parse info about')
            exit(code=1)

        filename = args.filename if args.filename else f'{args.username}-stats.csv'
        parse(args.username, filename, not args.hide_plots)
