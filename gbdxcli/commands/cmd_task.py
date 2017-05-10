import json
import click
from gbdxcli import pass_context, host


@click.group()
def task():
    """Task commands"""
    pass


# Required for dynamic import
cli = task

url_root = '%s/%s' % (host, 'workflows/v1')
task_url = url_root + '/tasks'
schema_url = url_root + '/schemas/TaskDescriptor'


@task.command('ls')
@click.option('--startswith','-s', type=click.STRING,
    help="Only return tasks that start with this substring")
@click.option('--contains','-c', type=click.STRING,
    help="Only return tasks that contain this substring")
@click.option('--endswith','-e', type=click.STRING,
    help="Only return tasks that end with this substring")
@pass_context
def list_tasks(ctx, startswith, contains, endswith):
    """List workflow tasks available to the user"""
    response = ctx.get(task_url).json()
    all_tasks = response['tasks']

    # Filter all tasks
    st_w_tasks = [task for task in all_tasks if startswith and task.startswith(startswith)]
    con_tasks = [task for task in all_tasks if contains and contains in str(task)]
    end_w_tasks = [task for task in all_tasks if endswith and task.endswith(endswith)]

    filtered_tasks = []
    if startswith:
        filtered_tasks = set(st_w_tasks)
    if contains:
        filtered_tasks = set(con_tasks) & set(filtered_tasks) if filtered_tasks else set(con_tasks)
    if endswith:
        filtered_tasks = set(end_w_tasks) & set(filtered_tasks)  if filtered_tasks else set(end_w_tasks)

    if filtered_tasks == []:
        filtered_tasks = all_tasks

    ctx.show(list(filtered_tasks))


@task.command('get')
@click.option('--name','-n', type=click.STRING,
    help="Name of task to describe")
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
@click.option('--name','-n', type=click.STRING,
    help="Name of task to delete")
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


@task.command('stdout')
@click.option('--task_id','-t', type=click.INT,
    help="Name of task")
@click.option('--workflow_id','-w', type=click.INT,
    help="Id of task")
@pass_context
def get_stdout(ctx, task_id, workflow_id):

    if task_id is None or workflow_id is None:
        ctx.show('Both task_id and workflow_id are required')
        return

    stdout_url = url_root + '/workflows/%s/tasks/%s/stdout' % (
        workflow_id, task_id
    )

    ctx.show(ctx.get(stdout_url))


@task.command('stderr')
@click.option('--task_id','-t', type=click.INT,
    help="Name of task")
@click.option('--workflow_id','-w', type=click.INT,
    help="Id of task")
@pass_context
def get_stderr(ctx, task_id, workflow_id):

    if task_id is None or workflow_id is None:
        ctx.show('Both task_id and workflow_id are required')
        return

    stdout_url = url_root + '/workflows/%s/tasks/%s/stderr' % (
        workflow_id, task_id
    )

    ctx.show(ctx.get(stdout_url))
