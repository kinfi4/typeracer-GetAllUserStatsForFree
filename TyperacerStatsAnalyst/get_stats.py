import argparse

from project_files.parser import Parser, Statistics


def parse(username, output_file):
    parser = Parser()
    stats = parser.parse_user_stats(username)
    stats.save_to_file(output_file)
    stats.plot_mean_wpm()


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-')
    arg_parser.add_argument('-u', '--username', help='Username of the account to parse info about')
