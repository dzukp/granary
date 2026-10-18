import json
from pathlib import Path


try:
    filename = str(Path(__file__).parent / 'settings.json')
    with open(filename, 'r') as f:
        settings = json.load(f)
except FileNotFoundError:
    settings = {}


COMPORT = settings.get('comport', 'COM3')
BAUDRATE = settings.get('baudrate', 9600)

# Пути к файлам (по умолчанию относительно app/)
BASE_PATH = Path(__file__).resolve().parent.parent
DB_PATH = settings.get('db_path', str(BASE_PATH / 'hmi/Data_granary/main.db'))
INIT_SQL_PATH = settings.get('init_sql_path', str(BASE_PATH / 'res/init.sql'))
ALARM_SOUND_PATH = settings.get('alarm_sound_path', str(BASE_PATH / 'res/alarm.wav'))
