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
