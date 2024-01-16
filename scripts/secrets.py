import os
import yaml
import scripts.file_utils as fu

base_dir = fu.get_root_dir()
secrets_path = os.path.join(base_dir, 'secrets.yaml')

def write_secrets():
    """Set up the secrets file"""
    with open(secrets_path, 'w') as f:
        yaml.safe_dump({'username': '', 'password': ''}, f)

def get_username():
    """Get the username from environment variables or YAML"""
    try:
        username = os.environ['DAVID_USERNAME']
    except:
        try:
            with open(secrets_path, 'r') as f:
                secrets = yaml.load(f, Loader=yaml.FullLoader)
                username = secrets['username']
        except:
            return None

    return username


def parse_secrets():
    """Get the username and password from environment variables or YAML"""
    try:
        username = os.environ['DAVID_USERNAME']
        password = os.environ['DAVID_PASSWORD']
    except:
        try:
            with open(secrets_path, 'r') as f:
                secrets = yaml.load(f, Loader=yaml.FullLoader)
                username = secrets['username']
                password = secrets['password']
        except:
            write_secrets()
            return None, None

    return username, password
