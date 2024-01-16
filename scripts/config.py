import os
import yaml
import scripts.file_utils as fu

base_dir = fu.get_root_dir()
config_path = os.path.join(base_dir, 'config.yaml')

def write_config():
    """Set up the config file"""
    refresh_rate = 0.1
    preserve_feed_position = False
    clear_logs = False
    config_dict = {
        'refresh_rate': refresh_rate,
        'preserve_feed_position': preserve_feed_position,
        'clear_logs': clear_logs
    }
    with open(config_path, 'w') as f:
        yaml.safe_dump(config_dict, f)

def read_config():
    """Read the config file"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
    except:
        write_config()
        return read_config()

    return config
