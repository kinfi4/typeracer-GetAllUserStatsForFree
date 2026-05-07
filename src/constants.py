URL = 'https://data.typeracer.com/pit/race_history?user=${user}&universe=play&n=100&cursor=${cursor}&startDate='

TYPERACER_BASE_URL = 'https://data.typeracer.com'
EXPORT_URL = 'https://data.typeracer.com/pit/export_data'

SCHEMA_COLUMNS = [
    'race', 'speed', 'accuracy', 'points', 'place', 'date',
    'datetime', 'mode', 'text_id', 'skill_level', 'universe',
]
EXTENDED_COLUMNS = ['datetime', 'mode', 'text_id', 'skill_level', 'universe']
