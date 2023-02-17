import yaml


def config_read():
    config = yaml.load(open('config.yml'), Loader=yaml.SafeLoader)
    return config
