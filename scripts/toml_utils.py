import tomllib
import os
import scripts.file_utils as fu

root_dir = fu.get_root_dir()
secrets_path = os.path.join(root_dir, 'secrets.toml')

def write_secrets():
    """Set up the secrets.toml file in the correct format"""
    with open(secrets_path, 'w') as f:
        f.write('[credentials]\n')
        f.write('username = ""\n')
        f.write('password = ""\n')

def parse_secrets(secrets):
    """Parse the secrets.toml file"""
    try:
        # Parse the secrets.toml file
        username = secrets['credentials']['username']
        password = secrets['credentials']['password']
        return username, password
    except:
        print('secrets.toml file is not formatted correctly. Please fix and run again.')
        write_secrets()
        exit()

def get_secrets():
    """Main function to get the secrets from the secrets.toml file"""
    # Try to open the secrets.toml file
    try:
        with open(secrets_path, 'rb') as f:
            secrets = tomllib.load(f)

        return parse_secrets(secrets)
    except:
        print('No secrets.toml file found. One has been created, please fill it out and run again.')
        write_secrets()
        exit()
