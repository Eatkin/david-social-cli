import os
from pathlib import Path

def get_root_dir():
    """Get the root directory of the project relative to the scripts folder ONLY"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_home_dir():
    """gets the home directory"""
    return str(Path.home())