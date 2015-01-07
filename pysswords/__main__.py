import os
import argparse


def default_db():
    return os.path.join(os.path.expanduser("~"), "~/.pysswords")


def parse_args(args):
    parser = argparse.ArgumentParser(prog="Pysswords")
    group_init = parser.add_argument_group("Init options")
    group_init.add_argument("-I", "--init", action="store_true")
    group_init.add_argument("-D", "--database", default=default_db())
    group_cred = parser.add_argument_group("Credential options")
    group_cred.add_argument("-a", "--add", action="store_true")
    group_cred.add_argument("-r", "--remove", action="store_true")
    group_cred.add_argument("-u", "--update", action="store_true")
    return parser.parse_args(args)
