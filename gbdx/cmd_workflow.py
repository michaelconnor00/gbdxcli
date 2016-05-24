import click
import json
from gbdxcli import pass_context, host


@click.group()
def workflow():
    pass


# Required for dynamic import
cli = workflow

url_root = '%s/%s' % (host, 'workflows/v1')
workflows_url = url_root + '/workflows'
schema_url = url_root + '/schemas/WorkflowDescriptor'


@workflow.command('list_tasks')
@pass_context
def list_tasks(ctx):
    """List workflow tasks available to the user"""
    ctx.show(ctx.gbdx.workflow.list_tasks())


@workflow.command('describe_task')
@click.option('--name','-n', type=click.STRING,
    help="Name of task to describe")
@pass_context
def describe_task(ctx, name):
    """Show the task description json for the task named"""
    ctx.show(ctx.gbdx.workflow.describe_task(name))


@workflow.command('status')
@click.option('--id','-i', type=click.STRING,
    help="ID of the workflow to status")
@click.option('--verbose', '-v', is_flag=True, help='Output a more detailed status of workflow')
@pass_context
def status(ctx, id, verbose):
    """Display the status information for the workflow ID given"""
    if not verbose:
        ctx.show(ctx.gbdx.workflow.status(id))
    else:
        response = ctx.get(workflows_url + '/' + id)
        r_dict = response.json()
        ctx.show('Worflow %s\n' % id)
        tasks = r_dict['tasks']
        for task in tasks:
            ctx.show({
                'name': task['name'],
                'state': task['state'],
                'note': task['note']
            })


@workflow.command('cancel')
@click.option('--id','-i', type=click.STRING,
    help="ID of the workflow to cancel")
@pass_context
def cancel_workflow(ctx, id):
    """Cancel the given workflow"""
    ctx.show(ctx.gbdx.workflow.cancel(id))


@workflow.command('launch')
@click.option('--filename', '-f', type=click.File('r'),
    help='Filename of workflow to launch (JSON file)')
@pass_context
def launch_workflow_from_file(ctx, filename):
    """Launch a workflow from a JSON file"""
    wf_dict = json.loads(filename.read())
    ctx.show(ctx.gbdx.workflow.launch(wf_dict))


@workflow.command('events')
@click.option('--id','-i', type=click.STRING,
    help="ID of the workflow")
@pass_context
def workflow_events(ctx, id):
    """Get the given workflows task events."""
    ctx.show(ctx.get('%s/%s/%s' %
        (workflows_url, id, 'events')
    ))


@workflow.command('schema')
@pass_context
def get_workflow_schema(ctx):
    """Get the workflow definition schema."""
    ctx.show(ctx.get(schema_url))


@workflow.command('search')
@click.option('--schema','-s', is_flag=True,
    help="Flag for returning the search schema")
@click.option('--lookback-hours', '-l', type=click.INT,
    help='Number of hours to lookback, 720hrs max.')
@click.option('--owner', '-o', type=click.STRING,
    help='Username of owner. Super user access required.')
@click.option('--state', '-s', type=click.STRING,
    help='Name of the state to filter by.')
@pass_context
def search(ctx, schema, lookback_hours, owner, state):
    if schema:
        ctx.show(ctx.get(workflows_url + '/search'))
    else:
        body = {
            "lookback_h": lookback_hours,
            "owner": owner,
            "state": state
        }
        ctx.show(ctx.post(
            
        ))
