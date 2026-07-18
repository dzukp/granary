from pylogic.tagsrv.module_dispatcher import SerialDispatcher
from pylogic.tagsrv.owen_m110 import OwenM110DiTcpModule, OwenM110DoTcpModule
from pylogic.tagsrv.tagsrv import InTag, OutTag

tags = {
    'in': {},
    'out': {},
}
modules = []


for i in range(1, 19):
    module_tags = [InTag(j) for j in range(1, 9)]
    modules.append(
        OwenM110DiTcpModule(
            ip='127.0.0.1',
            port=5020,
            slave=i,
            timeout=0.5,
            tags=module_tags,
            name=f'DI_{i:02}',
        ),
    )
    tags['in'].update({f'di_{i}_{tag.addr}': tag for tag in module_tags})


for i in range(21, 31):
    module_tags = [OutTag(j) for j in range(1, 9)]
    modules.append(
        OwenM110DoTcpModule(
            ip='127.0.0.1',
            port=5020,
            slave=i,
            timeout=0.5,
            tags=module_tags,
            name=f'DO_{i:02}',
        ),
    )
    tags['out'].update({f'do_{i}_{tag.addr}': tag for tag in module_tags})


tagsrv_config = {
    'tags': tags,
    'dispatchers': {'main': SerialDispatcher(modules=modules)},
}
