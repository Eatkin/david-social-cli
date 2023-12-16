import os

def get_root_dir():
    """Get the root directory of the project"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
