import click
import json
from gbdxcli import pass_context, host


@click.group()
def worker():
    """Workflow commands"""
    pass


# Required for dynamic import
cli = worker


@worker.command('run')
@click.option('--filename', '-f', type=click.File('r'),
    help='The workflow filename')
@pass_context
def run_workflow(ctx, filename):
    """
    Command to run a workflow locally
    """
