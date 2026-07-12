from .logged_object import DEFAULT_LOGGER
from .pyshell.rpcserver import start_shell_server
from .factory import Factory

import logging
import logging.config


def main(config):
    logging.basicConfig()
    app_config = {
        'objects': {},
        'simulators': {},
        'tagsrv_settings': {
            'tags': {},
            'sources': {},
            'dispatchers': {}},
        'supervisors': {}
    }
    app_config.update(config)

    if 'logging_conf' in app_config:
        logging.config.dictConfig(app_config['logging_conf'])

    if 'factory_class' in app_config:
        factory_ = config['factory_class']()
    else:
        factory_ = Factory()

    if 'controller_class' in app_config:
        factory_.set_controller_class(app_config['controller_class'])
    if 'tagsrv_class' in app_config:
        factory_.set_controller_class(app_config['tagsrv_class'])
    if 'saver_class' in app_config:
        factory_.set_saver_class(app_config['saver_class'])
    if 'supervisor_manager_class' in app_config:
        factory_.set_supervisor_manager_class(app_config['supervisor_manager_class'])

    top_object = factory_.get_top_object(app_config['objects'])
    sim_object = factory_.get_simulator_object(app_config['simulators'])
    sim_channels = sim_object.get_all_channels() if sim_object else {}
    tag_srv = factory_.get_tag_srv(config['tagsrv_settings'], top_object.get_all_channels(), sim_channels)
    saver = factory_.get_saver()
    supervisor_manager = factory_.get_supervisor_manager()
    for name, supervisor_class in app_config['supervisors'].items():
        factory_.add_supervisor(name, supervisor_class)

    controller = factory_.get_controller()
    controller.set_tag_server(tag_srv)
    controller.set_top_object(top_object)
    controller.set_sim_object(sim_object)
    controller.set_saver(saver)
    controller.set_supervisor_manager(supervisor_manager)

    if 'pyshell' not in config or config['pyshell']:
        start_shell_server(namespace=locals())

    controller.init()
    controller.start_loop()


if __name__ == '__main__':
    main({})
