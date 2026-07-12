from os import getcwd, makedirs
from pathlib import Path

from pylogic.main import main
from pylogic.modbus_supervisor import ModbusSupervisor
from objects import objects
from tagsrv_settings import tagsrv_config
from logconfig import logging_config
from rpc_supervisor import RpcSupervisor


def start():
    log_dir = Path(getcwd()) / 'logs'
    if not log_dir.exists():
        makedirs(log_dir.absolute())
    config = {
        'objects': objects,
        'tagsrv_settings': tagsrv_config,
        'logging_conf': logging_config,
        'supervisors': {'supervis_modbus': ModbusSupervisor, 'supervis_rpc': RpcSupervisor}
    }
    main(config)


if __name__ == '__main__':
    start()
