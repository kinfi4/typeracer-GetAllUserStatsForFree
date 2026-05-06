import io
import zipfile

import pandas as pd
from dateutil.parser import parse as parse_datetime


class ExportParser:
    COLUMNS = ['race', 'speed', 'accuracy', 'points', 'place', 'date']

    def parse_zip(self, zip_bytes: bytes) -> pd.DataFrame:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            csv_bytes = zf.read(zf.namelist()[0])

        raw = pd.read_csv(io.StringIO(csv_bytes.decode('utf-8')))

        return pd.DataFrame({
            'race': raw['Race #'].astype(str),
            'speed': raw['WPM'].round(2).astype(str),
            'accuracy': (raw['Accuracy'] * 100).round(2).astype(str),
            'points': raw['Points'].round(2).astype(str),
            'place': raw['Rank'].astype(str) + '/' + raw['# Racers'].astype(str),
            'date': raw['Date/Time (UTC)'].apply(lambda s: parse_datetime(s).date()),
        })
