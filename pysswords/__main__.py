import os
import argparse


def default_db():
    return os.path.join(os.path.expanduser("~"), "~/.pysswords")


def parse_args(args):
    parser = argparse.ArgumentParser(prog="Pysswords")
    parser.add_argument("-I", "--init", action="store_true")
    return parser.parse_args(args)
