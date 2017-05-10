import click
import json
from gbdxcli import pass_context, host
import arrow


@click.group()
def workflow():
    """Workflow commands"""
    pass


# Required for dynamic import
cli = workflow


url_root = '%s/%s' % (host, 'workflows/v1')
workflows_url = url_root + '/workflows'
schema_url = url_root + '/schemas/WorkflowDescriptor'


@workflow.command('ls')
@pass_context
def list_workflows(ctx):
    """Get a list of all workflows."""
    ctx.show(ctx.get(workflows_url))


@workflow.command('status')
@click.argument('id', nargs=-1, type=click.INT)
@click.option('--verbose', '-v', is_flag=True,
    help='Output a more detailed status of workflow')
@click.option('--runtime', '-r', is_flag=True,
    help='Output runtime with verbose output.')
@pass_context
def status(ctx, id, verbose, runtime):
    """Display the status information for the workflow ID(s) given."""
    id = [str(i) for i in id]
    is_multistatus = len(id) > 1
    if not verbose:
        if is_multistatus:
            'Return multistatuses'
            r = ctx.post(workflows_url + '/multistatus', data=json.dumps(id))
            ctx.show(build_workflows_status(ctx.raise_or_response(r), less=True))
        else:
            'Return single status'
            ctx.show(ctx.gbdx.workflow.status(id[0]))
    else:
        events_dict = None
        if is_multistatus:
            'Get multistatuses'
            response = ctx.post(workflows_url + '/multistatus', data=json.dumps(id))
            r_dict = ctx.raise_or_response(response)
        else:
            'Get single status'
            response = ctx.get(workflows_url + '/' + id[0])
            r_dict = [ctx.raise_or_response(response)]
            if runtime:
                r = ctx.get(workflows_url + '/' + id[0] + '/events')
                events_dict = ctx.raise_or_response(r)

        ctx.show(build_workflows_status(r_dict, events_dict))


def build_workflows_status(api_status, events, less=False):
    """
    Build and show the status for the provided workflow(s)
    :param api_status: a list of workflow statuses, or a single workflow status.
    """

    if not isinstance(api_status, list):
        api_status = [api_status]

    output_str = []

    # Show verbose info for workflow and tasks
    for wf in api_status:

        if less:
            # Parse workflow detials only
            output_str.append({'Workflow %s' % wf['id']: wf['state']})
        else:
            task_list = []
            wf_start_time = None
            # Parse task details
            for task in wf['tasks']:
                task_detail = {
                    'id': task['id'],
                    'name': task['name'],
                    'state': task['state'],
                    'note': task['note'],
                    'start time': task['start_time']
                }

                task_start_time = arrow.get(task['start_time'])
                if wf_start_time is None or task_start_time < wf_start_time:
                    if task_start_time is not None:
                        wf_start_time = task_start_time

                if events is not None:
                    task_detail['runtime'] = calc_runtime(task['name'], events['Events'])

                task_list.append(task_detail)

            output_str.append({
                'Worflow %s' % wf['id']: {
                    'Tasks': task_list,
                    'Status': wf['state'],
                    'Submitted Time': wf['submitted_time'],
                    'Runtime': str(arrow.get(wf['completed_time']) - wf_start_time)
                }
            })

    return output_str


def calc_runtime(task_name, events):
    """Calculate the runtime of the task name"""
    start_time = None
    end_time = None

    for event in events:
        if event['task'] == task_name:
            state = event['state']
            if state == 'running':
                start_time = arrow.get(event['timestamp'])
            elif state == 'complete':
                end_time = arrow.get(event['timestamp'])

    if not all([start_time, end_time]):
        return 'Task did not Run'

    return str(end_time - start_time)


@workflow.command('cancel')
@click.argument('id', nargs=1, type=click.INT)
@pass_context
def cancel_workflow(ctx, id):
    """Cancel the given workflow ID"""
    ctx.show(ctx.gbdx.workflow.cancel(str(id)))


@workflow.command('launch')
@click.option('--filename', '-f', type=click.File('r'),
    help='Filename of workflow to launch (JSON file)')
@pass_context
def launch_workflow_from_file(ctx, filename):
    """Launch a workflow from a JSON file"""
    wf_dict = json.loads(filename.read())
    ctx.show(ctx.gbdx.workflow.launch(wf_dict))


@workflow.command('events')
@click.argument('id', nargs=1, type=click.INT)
@pass_context
def workflow_events(ctx, id):
    """Get the given workflow ID task events."""
    ctx.show(ctx.get('%s/%s/%s' %
        (workflows_url, id, 'events')
    ))


@workflow.command('get')
@click.argument('id', nargs=1, type=click.INT)
@pass_context
def workflow_details(ctx, id):
    """Get the given workflow ID details."""
    ctx.show(ctx.get('%s/%s' %
        (workflows_url, id)
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
@click.option('--state', '-s', type=click.Choice([
        'all', 'submitted', 'scheduled', 'started', 'canceled',
        'cancelling', 'failed', 'succeeded', 'timedout',
        'pending','running', 'complete'
    ]),
    help='Name of the state to filter by.')
@pass_context
def search(ctx, schema, lookback_hours, owner, state):
    """Search workflow database by lookback time, owner, or state."""
    search_url = workflows_url + '/search'
    if schema:
        ctx.show(ctx.get(search_url))
    else:
        body = {
            "lookback_h": lookback_hours,
            "owner": owner,
            "state": state
        }

        # Remove keys with None values
        post_data = {k:v for k, v in body.iteritems() if v is not None}

        ctx.show(ctx.post(
            search_url,
            data=json.dumps(post_data)
        ))
