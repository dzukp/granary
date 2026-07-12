from os import getcwd, makedirs
from pathlib import Path
import json

from pylogic.logged_object import LoggedObject


class FileParameterSaver(LoggedObject):

    def __init__(self):
        super().__init__()
        self.work_dir = Path(getcwd())
        self.save_subdir = 'saves/'
        self.save_dir = self.work_dir / self.save_subdir

    def save(self, name, data):
        if data:
            filename = self.filename(name)
            if not self.save_dir.exists():
                makedirs(self.save_dir.absolute())
            with open(filename, 'w') as fl:
                json.dump(data, fl)
                self.logger.info(f'{name} saved')
                self.logger.debug(f'{name} saved data: {data}')

    def load(self, name):
        try:
            with open(self.filename(name), 'r') as fl:
                data = json.load(fl)
                self.logger.info(f'{name} loaded')
                self.logger.debug(f'{name} loaded data: {data}')
                return data
        except FileNotFoundError:
            self.logger.info(f'file for `{name}` not exists, skip')
        except json.decoder.JSONDecodeError:
            self.logger.info(f'file for `{name}` has no json content, skip')

    def set_subdir(self, dirname):
        self.save_subdir = dirname
        self.save_dir = self.work_dir / self.save_subdir

    def filename(self, name):
        return self.save_dir / (name + '.sav')

