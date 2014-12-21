import argparse


def get_args(command_args=None):
    """Return args from command line"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", nargs="?", const=".pysswords")
    args = parser.parse_args(command_args)
    return args
