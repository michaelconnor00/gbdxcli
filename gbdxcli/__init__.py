__version__ = '0.0.3'

import click
from gbdxcli.context import CommandContext
import os


pass_context = click.make_pass_decorator(CommandContext, ensure=True)
host = 'https://%s/' % os.environ.get('GBDXTOOLS_HOST','geobigdata.io')
