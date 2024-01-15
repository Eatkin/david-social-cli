import os
import yaml
import scripts.file_utils as fu

base_dir = fu.get_root_dir()
secrets_path = os.path.join(base_dir, 'secrets.yaml')

def write_secrets():
    """Set up the envrc file"""
    with open(secrets_path, 'w') as f:
        yaml.dump({'username': 'username', 'password': 'password'}, f)


def parse_secrets():
    """Get the username and password from environment variables"""
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
