"""AWS CloudFormation utilities"""

import os.path
import subprocess

def _make_params(params):
    """Convert the params dict (from parameter name to parameter value) into a
    list of words ready to be passed to an `aws cloudformation` command,
    including the `--parameters` word at the beginning."""
    return [ "--parameters" ] \
         + [ "ParameterKey={},ParameterValue={}".format(k, params[k])
                 for k in params ]

def _create_or_update(command, template, stack_name, params, quiet, noop):
    template_url = "file://" + os.path.abspath(template)
    params = _make_params(params)
    cmd = [ 'aws', 'cloudformation', command,
            "--stack-name", stack_name,
            "--template-body", template_url,
            "--capabilities", "CAPABILITY_IAM",
          ] + params
    cmd_str = " ".join(cmd)
    if noop and not quiet:
        print("If --noop had not been specified, I would execute this command:")
        print(cmd_str)
    elif not quiet:
        print("I am about to execute this aws command:")
        print(cmd_str)
    if not noop:
        subprocess.call(cmd)

def create_stack(*args):
    _create_or_update('create-stack', *args)

def update_stack(*args):
    _create_or_update('update-stack', *args)
