'''
Authors: Donnie Marino
Contact: dmarino@digitalglobe.com

Command Line interface for the GBDX tools suite.
This is intended to mimic the aws cli in that users
won't need to program to access the full functionality
of the GBDX API.

This is a Click application
Click is the 'Command Line Interface Creation Kit'
Learn more at http://click.pocoo.org/5/

Main gbdx command group is cli
Subcommands are click groups

Commands belong to one click group, allows for cli syntax like this:
gbdx workflow list_tasks
gbdx workflow describe_task -n MutualInformationCoregister
gbdx catalog strip_footprint -c 10200100359B2C00
'''

import click

from gbdx.command_loader import CommandLoader
from gbdx.context import CommandContext


pass_context = click.make_pass_decorator(CommandContext, ensure=True)
host = 'https://geobigdata.io/'


# Main command group
@click.command(cls=CommandLoader)
def cli():
    """GBDX Command Line Interface
    example:
        gbdx workflow list_tasks
    """
    pass
