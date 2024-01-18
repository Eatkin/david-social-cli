import os
from cryptography.fernet import Fernet
import scripts.file_utils as fu

base_dir = fu.get_root_dir()
home_dir = fu.get_home_dir()
key_path = os.path.join(home_dir, '.david.key')
cred_path = os.path.join(home_dir, '.david.cred')
username_cache = os.path.join(base_dir, 'username.txt')

def key_gen():
    """Generate a key for encrypting credentials"""
    key = Fernet.generate_key()
    with open(key_path, 'wb') as f:
        f.write(key)

def get_key():
    """Get the key for encrypting credentials"""
    try:
        with open(key_path, 'rb') as f:
            key = f.read()
        return key
    except:
        key_gen()
        return get_key()

def encrypt_credentials(credentials, key):
    cipher_suite = Fernet(key)
    encrypted_credentials = cipher_suite.encrypt(credentials.encode())
    return encrypted_credentials

def decrypt_credentials(encrypted_credentials, key):
    cipher_suite = Fernet(key)
    decrypted_credentials = cipher_suite.decrypt(encrypted_credentials).decode()
    return decrypted_credentials

def write_secrets(username, password):
    """Set up the secrets file"""
    key = get_key()
    encrypted_credentials = encrypt_credentials(f"{username}:{password}", key)
    with open(cred_path, 'wb') as f:
        f.write(encrypted_credentials)

def get_username():
    """Get the username"""
    username = parse_secrets()[0]
    if username is not None:
        return username

    try:
        with open(username_cache, 'r') as f:
            username = f.read()
        return username
    except:
        return None


def parse_secrets():
    """Get the username and password"""
    try:
        with open(cred_path, 'rb') as f:
            encrypted_credentials = f.read()
        key = get_key()
        credentials = decrypt_credentials(encrypted_credentials, key)
        username, password = credentials.split(":")
    except:
        username, password = None, None

    return username, password
