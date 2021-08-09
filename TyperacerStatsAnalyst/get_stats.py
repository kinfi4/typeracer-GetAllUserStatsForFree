from project_files.parser import Parser, Statistics


# parser = Parser()
# stats = parser.parse_user_stats('kinfi4')
#
# stats.save_to_file('mystats.csv')
# print(stats.user_stats[1])
# print(stats.user_stats[2])

stats = Statistics.get_stats_from_csv('mystats.csv')



