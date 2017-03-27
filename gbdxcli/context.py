import sys
import os
import json
import click
from gbdxtools import Interface


class APIError(Exception):
    pass


class CommandContext(object):
    """
    Class to encapsulate common session context for the cli commands.
    """

    def __init__(self):
        host = os.environ.get('GBDXTOOLS_HOST', None)
        config = os.environ.get('GBDXTOOLS_PROFILE', None)
        self.gbdx = Interface(host=host, config_file=config)
        self.session = self.gbdx.gbdx_connection

    def get(self, url):
        return self.session.get(url)

    def post(self, url, data):
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        return self.session.post(url, data=data, headers=headers)

    def put(self, url, data):
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        return self.session.put(url, data=data, headers=headers)

    @staticmethod
    def raise_or_response(response, parse=True):
        if response.status_code >= 400:
            raise APIError(response.text)

        if parse:  # Parse from JSON adn return
            return response.json()
        else:
            return response.text

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
