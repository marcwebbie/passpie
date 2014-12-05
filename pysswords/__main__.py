import argparse

parser = argparse.ArgumentParser()
parser.add_argument('path')


def main(args=None):
    with open(args.path, "w") as f:
        pass

if __name__ == "__main__":
    main(parser.parse_args())
