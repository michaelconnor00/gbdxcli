__version__ = '0.0.3'

import click
from gbdxcli.context import CommandContext


pass_context = click.make_pass_decorator(CommandContext, ensure=True)
host = 'https://geobigdata.io/'
