import os
import shutil
import click
import json
import subprocess
# import tempfile
from docker import Client
# import jsonschema

from gbdxcli import pass_context, host


@click.group()
def worker():
    """Workflow worker commands"""
    pass


# Required for dynamic import
cli = worker


url_root = '%s/%s' % (host, 'workflows/v1')
workflows_url = url_root + '/workflows'
wf_schema_url = url_root + '/schemas/WorkflowDescriptor'
task_url = url_root + '/tasks'


class TaskAPIError(Exception):
    pass

class WorkflowAPIError(Exception):
    pass

class InvalidPortError(Exception):
    pass


@worker.command('run')
@click.option('--filename', '-f', type=click.File('r'),
    help='The filename for the workflow to run locally.')
@click.option('--output-dir','-o', type=click.STRING,
    help="Provide string path for destination of the tasks output.")
@click.option('--verbose', '-v', is_flag=True,
    help='Output a more detailed status of workflow.')
@click.option('--pull', '-p', is_flag=True,
    help='Pull the latest image from Docker hub before creating a container.')
@click.option('--del-output', '-d', is_flag=True,
    help='Delete the output folder after execution.')
@pass_context
def run_workflow(ctx, filename, output_dir, verbose, pull, del_output):
    """
    Command to run a workflow locally
    """
    dkr = Client(timeout=3600)

    # workflow_schema = ctx.get(wf_schema_url).json()
    # print(workflow_schema)

    wf_json = filename.read()

    # Validate the workflow definition
    # jsonschema.validate(wf_json, workflow_schema)

    wf_dict = json.loads(wf_json)

    # task_exec_list = wf_dict['tasks']
    # task_exec_list.sort(cmp=_compare_task_dependencies)
    # task_exec_list = _sort_by_task_dependencies(task_exec_list)
    # ctx.show('Post: ')
    # ctx.show(task_exec_list)

    task = wf_dict['tasks'][0]  # TODO This only works for one task.

    response = ctx.get('%s/%s' % (task_url, task['taskType']))

    if response.status_code != 200:
        raise TaskAPIError(response.text)

    task_def = response.json()

    # Only support docker
    if len([x['type'] for x in task_def['containerDescriptors'] if x['type'] != 'DOCKER']) > 0:
        raise ValueError("Worker only supports DOCKER tasks")

    # Pull the docker container
    img = task_def['containerDescriptors'][0]['properties']['image']

    # Map input and output volumes
    # input_path = os.path.join(os.getcwd(), 'inputs')
    # input_path = tempfile.mkdtemp()
    if output_dir is None:
        output_path = os.path.join(os.getcwd(), '%s_outputs' % wf_dict['name'])
    else:
        # Add support for absolute and relative paths.
        raise NotImplementedError()

    cont_input_path = os.path.join(os.path.sep, 'mnt', 'work', 'input')
    cont_output_path = os.path.join(os.path.sep, 'mnt', 'work', 'output')

    # _check_or_create_dir(input_path)
    _check_or_create_dir(output_path)

    vol_mnts = []
    vol_binds = []

    string_input_ports = {}

    for port in task['inputs']:
        # Use workflow value if it is a valid path.

        task_port = [p['type'] for p in task_def['inputPortDescriptors'] if p['name'] == port['name'] or port['name'].startswith(p['name'])]

        if len(task_port) == 0:
            raise InvalidPortError('Port name not found in task definition')

        if task_port[0] == 'directory':
            # Check if abs path
            if os.path.isabs(port['value']) and os.path.isdir(port['value']):
                dest_path = port['value']
            # Check if relative path
            elif os.path.isabs(os.path.join(os.getcwd(), port['value'])) and \
                os.path.isdir(os.path.join(os.getcwd(), port['value'])):
                dest_path = os.path.join(os.getcwd(), port['value'])
            # Use std input path from cwd.
            else:
                dest_path = os.path.join(os.getcwd(), 'inputs', port['name'])
                if not os.path.isdir(dest_path):
                    raise InvalidPortError("Directory type input ports must be a valid directory")

            cont_path = os.path.join(cont_input_path, port['name'])
            vol_mnts.append(cont_path)
            vol_binds.append(
                '%s:%s:rw' % (dest_path, cont_path)
            )
        else:
            string_input_ports['gbdx-input-port-' + port['name']] = port.get('value')

    for port in task['outputs']:
        # Write all outputs to CWD
        dest_path = os.path.join(output_path, port['name'])
        cont_path = os.path.join(cont_output_path, port['name'])
        vol_mnts.append(cont_path)
        vol_binds.append(
            '%s:%s:rw' % (dest_path, cont_path)
        )

    cont_args = {
        "image": img,
        "volumes": vol_mnts,
        "host_config": dkr.create_host_config(binds=vol_binds),
        "environment": string_input_ports
    }

    if 'command' in task_def['containerDescriptors'][0].keys():
        cont_args['command'] = task_def['containerDescriptors'][0]['command']

    if verbose:
        print('Container Args: %s\n' % cont_args)

    container_id = dkr.create_container(**cont_args)

    if verbose:
        print('Container ID: %s\n' % container_id)

    if pull:
        print('Pulling Latest Image')
        dkr.pull(img)

    print('Container Starting')
    dkr.start(container_id.get('Id'))
    dkr.wait(container_id.get('Id'))
    print('Container Stopped\n')

    # Copy ports.json to output
    cnt_id_and_src_path = '%s:%s' % (container_id.get('Id'), os.path.join(cont_output_path, 'ports.json'))
    try:
        subprocess.check_call(['docker', 'cp', cnt_id_and_src_path, output_path])
    except subprocess.CalledProcessError:
        print("No output ports.json found")

    output = dkr.logs(
        container=container_id.get('Id'),
        stdout=True,
        stderr=True
    ).decode("utf-8")

    print('Container Output:\n')
    print(output)
    print('\t--End Output--')

    # shutil.rmtree(input_path)
    if del_output:
        shutil.rmtree(output_path)

    print('Stop and Remove Container')
    dkr.remove_container(container_id.get('Id'))


def _check_or_create_dir(full_path):
    """
    Remove existsing output folder, make a new output dir.
    """
    try:
        shutil.rmtree(full_path)
    except OSError as e:
        if 'No such file or directory' not in e.strerror:
            raise e
    finally:
        os.makedirs(full_path)

#### For running more than one task.

# def _sort_by_task_dependencies(task_list):
#     for i, task in enumerate(task_list):
#
#         if _num_input_deps(task['inputs']) == 0:
#             continue
#
#         for dep_task_name in [x['source'].split(':')[0] for x in task['inputs'] if 'source' in x.keys()]:
#
#             for task in task_list:
#                 if dep_task_name != task['name']:
#                     continue
#
#                 task_index = _get_task_index(task['name'], task_list)
#
#                 if i <= task_index:
#                     # Move the task back in the list_tasks
#                     task_to_move = task_list.pop(i)
#                     task_list.insert(task_index + 1, task_to_move)
#     return task_list
#
#
# def _get_task_index(task_name, task_list):
#     for x, task in enumerate(task_list):
#         if task['name'] == task_name:
#             return x
#     raise IndexError("task %s not found" % task_name)
#
#
# def _num_input_deps(inputs):
#     cnt = 0
#     for i in inputs:
#         if 'source' in i.keys():
#             cnt+=1
#     return cnt
#
#
# def _compare_task_dependencies(x, y):
#     x_num_deps = _num_input_deps(x['inputs'])
#
#     y_num_deps = _num_input_deps(y['inputs'])
#
#     if x_num_deps < y_num_deps:
#         return -1
#     elif x_num_deps == y_num_deps:
#         return 0
#     else:
#         return 1
