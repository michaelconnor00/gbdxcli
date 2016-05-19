import sys
import json
import click
from gbdxtools import Interface


class CommandContext(object):

    def __init__(self):
        self.gbdx = Interface()

    def get(self, url):
        return self.gbdx.gbdx_connection.get(url)

    def post(self, url, data):
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        return self.gbdx.gbdx_connection.post(url, data=data, headers=headers)

    def put(self, url, data):
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        return self.gbdx.gbdx_connection.put(url, data=data, headers=headers)

    def delete(self, url):
        return self.gbdx.gbdx_connection.delete(url)

    def log(self, msg, *args):
        """Logs a message to stderr."""
        if args:
            msg %= args
        click.echo(msg, file=sys.stderr)

    def show(self, data):
        """Output Formated JSON"""
        try:
            click.echo(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
        except TypeError:
            try:
                output = json.dumps(
                    json.loads(data.text),
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': ')
                )
            except ValueError:
                output = data.text
            click.echo(output)
