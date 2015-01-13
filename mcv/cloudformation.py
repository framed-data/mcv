"""AWS CloudFormation utilities"""

import os.path
import subprocess
import sys
import time
import json


def _make_params(params):
    """Convert the params dict (from parameter name to parameter value) into a
    list of words ready to be passed to an `aws cloudformation` command,
    including the `--parameters` word at the beginning."""
    return ["--parameters"] + \
           ["ParameterKey={0},ParameterValue={1}".format(k, params[k])
            for k in params]


def check_template(template, verbose=False):
    template_url = "file://" + os.path.abspath(template)
    cmd = ['aws', 'cloudformation', 'validate-template',
           "--template-body", template_url]
    cmd_str = " ".join(cmd)

    if verbose:
        print("I am about to execute this aws command:")
        print(cmd_str)

    # The command will output to STDOUT if successful, and STDERR if
    # unsuccessful, but we want neither output to be seen by the user.
    try:
        with open('/dev/null', 'w') as devnull:
            subprocess.call(cmd, stdout=devnull, stderr=devnull)
        return True
    except subprocess.CalledProcessError:
        return False


def get_stack_status(stack_name):
    query = "Stacks[?StackName==`" + stack_name + "`].StackStatus | [0]"
    cmd = ['aws', 'cloudformation', 'describe-stacks', "--query", query]
    return subprocess.Popen(
            cmd, stdout=subprocess.PIPE).communicate()[0].strip().strip('"')


def wait_for_stack_status(stack_name, desired_status, bad_status=None):
    status = get_stack_status(stack_name)
    while status != desired_status:
        if bad_status and status == bad_status:
            sys.stdout.write('\n')
            sys.stdout.flush()
            return False
        time.sleep(5)
        sys.stdout.write('.')
        sys.stdout.flush()
        status = get_stack_status(stack_name)
    sys.stdout.write('\n')
    return True


def wait_for_created_or_updated(verb, stack_name):
    sys.stdout.write("Waiting for stack " + stack_name +
                     " to be " + verb + "d.")
    sys.stdout.flush()
    desired_status = verb.upper() + '_COMPLETE'
    success = wait_for_stack_status(stack_name, desired_status,
                                    'ROLLBACK_COMPLETE')
    if not success:
        print("There was a problem, and the stack has been rolled back.")
        print("See the CloudFormation event log in the AWS console " +
              "for more info")


def wait_for_destroyed(stack_name):
    sys.stdout.write("Waiting for stack " + stack_name + " to be destroyed.")
    sys.stdout.flush()
    wait_for_stack_status(stack_name, '')


def get_current_params(stack_name):
    command = ["aws", "cloudformation", "describe-stacks",
               "--stack-name", stack_name]
    output = subprocess.Popen(command, stdout=subprocess.PIPE).communicate()[0]
    params = json.loads(output)['Stacks'][0]['Parameters']
    return dict((p['ParameterKey'], p['ParameterValue']) for p in params)


def load_params(stack_name, params):
    # If any of the parameters are specified on the command-line, those values
    # should overwrite what's currently in the stack.
    curr_params = get_current_params(stack_name)
    # Merge the dicts, preferring the latter dict in case of a key conflict.
    return dict(curr_params.items() + params.items())


def create_or_update(verb, template, stack_name, params, quiet, noop, wait):
    template_url = "file://" + os.path.abspath(template)
    params = _make_params(params)
    command = 'create-stack' if verb == 'create' else 'update-stack'
    cmd = ['aws', 'cloudformation', command,
           "--stack-name", stack_name,
           "--template-body", template_url,
           "--capabilities", "CAPABILITY_IAM"] + params
    cmd_str = " ".join(cmd)

    if noop and not quiet:
        print("If noop had not been specified, I would execute this command:")
        print(cmd_str)
    elif not quiet:
        print("I am about to execute this aws command:")
        print(cmd_str)
    if not noop:
        subprocess.call(cmd)
        if wait:
            wait_for_created_or_updated(verb, stack_name)


def create(template, stack_name, params, quiet, noop, wait):
    create_or_update('create', template, stack_name, params, quiet, noop, wait)


def update(template, stack_name, params, quiet, noop, wait):
    create_or_update('update', template, stack_name, params, quiet, noop, wait)


def destroy(stack_name, quiet=False, noop=False, wait=False):
    cmd = ['aws', 'cloudformation', 'delete-stack',
           "--stack-name", stack_name]
    cmd_str = " ".join(cmd)

    if noop and not quiet:
        print("If noop had not been specified, I would execute this command:")
        print(cmd_str)
    elif not quiet:
        print("I am about to execute this aws command:")
        print(cmd_str)
    if not noop:
        subprocess.call(cmd)
        if wait:
            wait_for_destroyed(stack_name)
