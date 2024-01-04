import os
import scripts.file_utils as fu

base_dir = fu.get_root_dir()
secrets_path = os.path.join(base_dir, '.envrc')

def write_secrets():
    """Set up the envrc file"""
    with open(secrets_path, 'w') as f:
        f.write('export DAVID_USERNAME=""\n')
        f.write('export DAVID_PASSWORD=""\n')

def parse_secrets():
    """Get the username and password from environment variables"""
    try:
        username = os.environ['DAVID_USERNAME']
        password = os.environ['DAVID_PASSWORD']
    except:
        print('Environment variables DAVID_USERNAME and DAVID_PASSWORD not set.')
        print('Please set them in the .envrc file.')
        write_secrets()
        exit(1)

    return username, password
