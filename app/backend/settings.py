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

ALARM_SOUND_PATH = settings.get(
    'alarm_sound_path', str(Path(__file__).resolve().parent.parent / 'res/alarm.wav')
)

DB_PATH = settings.get(
    'db_path', str(Path(__file__).resolve().parent.parent / 'hmi/Data_granary/main.db')
)
DB_INIT = settings.get(
    'db_init', str(Path(__file__).resolve().parent.parent / 'res/init.sql')
)

TREND_FLUSH_INTERVAL = settings.get('trend_flush_interval', 1.0)
TREND_CLEANUP_INTERVAL = settings.get(
    'trend_cleanup_interval', 7 * 24 * 3600
)  # сек, 7 дней
TREND_CLEANUP_RETENTION = settings.get(
    'trend_cleanup_retention', 60 * 24 * 3600
)  # сек, 60 дней
