import click
from gbdxcli import pass_context


@click.group()
def workflow():
    pass


# Required for dynamic import
cli = workflow


@workflow.command()
@pass_context
def list_tasks(ctx):
    """List workflow tasks available to the user"""
    ctx.show( ctx.gbdx.workflow.list_tasks() )


@workflow.command()
@click.option('--name','-n',
    help="Name of task to describe")
@pass_context
def describe_task(ctx, name):
    """Show the task description json for the task named"""
    ctx.show( ctx.gbdx.workflow.describe_task(name) )


@workflow.command()
@click.option('--id','-i',
    help="ID of the workflow to status")
@pass_context
def status(ctx, id):
    """Display the status information for the workflow ID given"""
    ctx.show( ctx.gbdx.workflow.status(id) )
