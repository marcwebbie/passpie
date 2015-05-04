from tabulate import tabulate
import click


class Table(object):

    def __init__(self, headers, table_format='rst', colors=None, hidden=None):
        self.headers = headers
        self.colors = colors if colors else {}
        self.hidden = hidden if hidden else []
        self.table_format = table_format

    def colorize(self, key, text):
        return click.style(text, fg=self.colors.get(key))

    def render(self, data):
        rows = []
        for entry in data:
            row = []
            for header in self.headers:
                if header in self.hidden:
                    entry[header] = '*****'
                elif header in self.colors:
                    text = entry[header]
                    entry[header] = self.colorize(header, text)
                row.append(entry[header])
            rows.append(row)

        headers = [click.style(h.title(), bold=True) for h in self.headers]
        return tabulate(rows, headers, tablefmt=self.table_format)
