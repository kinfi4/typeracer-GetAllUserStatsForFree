from project_files.parser import Parser, Statistics


# parser = Parser()
# stats = parser.parse_user_stats('kinfi4')
#
# stats.save_to_file('mystats.csv')

stats = Statistics.get_stats_from_csv('mystats.csv')
print(stats.user_stats)
stats.plot_mean_wpm()


