from project_files.parser import Parser


parser = Parser()
stats = parser.parse_user_stats('kinfi4')

print(len(stats.user_stats))
print(stats.user_stats)
stats.save_to_file('mystats.csv')
# print(stats.user_stats[1])
# print(stats.user_stats[2])
