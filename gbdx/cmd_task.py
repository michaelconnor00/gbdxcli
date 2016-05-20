import json
import click
from gbdxcli import pass_context, host


@click.group()
def task():
    pass


# Required for dynamic import
cli = task

url_root = '%s/%s' % (host, 'workflows/v1')
task_url = url_root + '/tasks'
schema_url = url_root + '/schema/TaskDescriptor'


@task.command('ls')
@pass_context
def list_tasks(ctx):
    """List workflow tasks available to the user"""
    ctx.show( ctx.get(task_url) )


@task.command('get')
@click.option('--name','-n', help="Name of task to describe")
@pass_context
def describe_task(ctx, name):
    """Show the task description json for the task named"""
    url = task_url + '/' + name
    ctx.show( ctx.get(url) )


@task.command('register')
@click.option('--filename', '-f', type=click.File('r'),
    help='Filename of task to register (JSON file)')
@pass_context
def register_task_from_file(ctx, filename):
    """Register a task from a JSON file"""
    task_dict = json.loads(filename.read())
    ctx.show(ctx.post(task_url, data=json.dumps(task_dict)))


@task.command('delete')
@click.option('--name','-n', help="Name of task to delete")
@pass_context
def delete_task(ctx, name):
    """Delete the named Task from the platform"""
    url = task_url + '/' + name
    ctx.show(ctx.delete(url))


@task.command('schema')
@pass_context
def get_task_schema(ctx):
    """Get the schema for Task definitions"""
    ctx.show(ctx.get(schema_url))
