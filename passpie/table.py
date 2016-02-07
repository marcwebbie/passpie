from tabulate import tabulate
import click


class Table(object):

    def __init__(self, headers,
                 table_format='rst',
                 colors=None,
                 hidden=None,
                 missing=None,
                 hidden_string="*****"):
        self.headers = headers
        self.colors = colors if colors else {}
        self.hidden = hidden if hidden else []
        self.hidden_string = hidden_string
        self.table_format = table_format
        self.missing = missing

    def colorize(self, key, text):
        return click.style(text, fg=self.colors.get(key))

    def render(self, data):
        data = sorted(data, key=lambda c: c[self.headers[0]])
        rows = []
        for entry in data:
            row = []
            for header in self.headers:
                if header in self.hidden:
                    entry[header] = self.hidden_string
                elif header in self.colors:
                    text = entry[header]
                    entry[header] = self.colorize(header, text)
                row.append(entry[header])
            rows.append(row)

        headers = [click.style(h.title(), bold=True) for h in self.headers]
        if rows:
            return tabulate(rows,
                            headers,
                            tablefmt=self.table_format,
                            missingval=self.missing,
                            numalign='left')
