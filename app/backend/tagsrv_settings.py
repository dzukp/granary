from pylogic.tagsrv.module_dispatcher import SerialDispatcher
from pylogic.tagsrv.owen_m110 import OwenM110DiModule, OwenM110DoModule
from pylogic.tagsrv.tagsrv import InTag, OutTag
from pylogic.tagsrv.serialsource import SerialSource

tags = {
    'in': {},
    'out': {},
}
modules = []


serial_source = SerialSource(
    port='COM3',
    baudrate=9600,
)


for i in range(1, 19):
    module_tags = [InTag(j) for j in range(1, 9)]
    modules.append(
        OwenM110DiModule(
            # ip='127.0.0.1',
            # port=5020,
            serial=serial_source.serial,
            slave=i,
            timeout=0.1,
            tags=module_tags,
            name=f'DI_{i:02}',
        ),
    )
    tags['in'].update({f'di_{i}_{tag.addr}': tag for tag in module_tags})


for i in range(21, 31):
    module_tags = [OutTag(j) for j in range(1, 9)]
    modules.append(
        OwenM110DoModule(
            # ip='127.0.0.1',
            # port=5020,
            serial=serial_source.serial,
            slave=i,
            timeout=0.1,
            tags=module_tags,
            name=f'DO_{i:02}',
        ),
    )
    tags['out'].update({f'do_{i}_{tag.addr}': tag for tag in module_tags})


tagsrv_config = {
    'tags': tags,
    'dispatchers': {'main': SerialDispatcher(modules=modules)},
}
