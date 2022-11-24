import os
import hydra

from hydra import compose


config_dir = os.getenv('CONFIG_DIR', None)

if config_dir is None:
    config_dir = os.path.dirname(__file__)
else:
    config_dir = os.path.join(os.getcwd(), config_dir)

hydra.initialize_config_dir(config_dir)
dialogflow_config = compose(config_name='dialogflow')
