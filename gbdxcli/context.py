import sys
import json
import click
from gbdxtools import Interface
from gbdx_auth import gbdx_auth


class CommandContext(object):
    """
    Class to encapsulate common session context for the cli commands.
    """

    def __init__(self):
        self.session = gbdx_auth.get_session()
        self.gbdx = Interface(gbdx_connection=self.session)

    def get(self, url):
        return self.session.get(url)

    def post(self, url, data):
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        return self.session.post(url, data=data, headers=headers)

    def put(self, url, data):
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        return self.session.put(url, data=data, headers=headers)

    def delete(self, url):
        return self.session.delete(url)

    def log(self, msg, *args):
        """Logs a message to stderr."""
        if args:
            msg %= args
        click.echo(msg, file=sys.stderr)

    def show(self, data, sort=True):
        """Output Formated JSON"""
        try:
            output = json.dumps(data, sort_keys=sort, indent=4, separators=(',', ': '))
        except TypeError:
            try:
                output = json.dumps(
                    json.loads(data.text),
                    sort_keys=sort,
                    indent=4,
                    separators=(',', ': ')
                )
            except ValueError:
                output = data.text
        click.echo(output)
