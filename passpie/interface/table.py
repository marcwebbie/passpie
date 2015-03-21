from collections import OrderedDict

import click
from tabulate import tabulate


class Table(object):

    def __init__(self, elems, headers):
        self.elems = elems.copy()
        self.headers = headers
        self.cols = OrderedDict()
        for header in headers:
            self.cols[header] = [e[header] for e in self.elems]

    @property
    def rows(self):
        return zip(*[self.cols[h] for h in self.headers])

    def copy(self):
        return Table(self.elems, self.headers)

    def __getitem__(self, headers):
        if isinstance(headers, str):
            headers = (headers,)
        return Table(self.elems, headers)

    def format(self, colors=None, hidden=(), fmt="simple", missing="*****"):
        table = self.copy()

        for hidden in [h for h in table.headers if h in hidden]:
            table.cols[hidden] = [missing for e in table.cols[hidden]]

        colors = colors if colors else {}
        for header, color in colors.items():
            table.cols[header] = [click.style(e, color) for e in table.cols[header]]

        return tabulate(table.rows,
                        headers=[h.title() for h in table.headers],
                        numalign='left',
                        tablefmt=fmt,
                        missingval=missing)

    def __str__(self):
        return self.format()


if __name__ == "__main__":
    people = [
        {"name": "Marc", "age": 27, "ville": "Recife", "country": "Brazil"},
        {"name": "Ankat", "age": 35, "ville": "Conde", "country": "France"},
        {"name": "Kenety", "age": 13, "ville": "Bethune", "country": "France"}
    ]
    fmt = "rst"
    colors = {"name": "yellow", "ville": "magenta", "country": "cyan"}
    hidden = ("ville",)

    t = Table(people, ("name", "age", "ville", "country"))
    click.echo(t["name", "age"])
    click.echo(t["name"])
    click.echo(t["name", "ville"])
    click.echo(t.format(colors=colors, hidden=hidden, fmt="fancy_grid"))
    click.echo(t.format(colors=colors, fmt="rst"))
