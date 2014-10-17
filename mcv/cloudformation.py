"""AWS CloudFormation utilities"""

import os.path
import subprocess


def _make_params(params):
    """Convert the params dict (from parameter name to parameter value) into a
    list of words ready to be passed to an `aws cloudformation` command,
    including the `--parameters` word at the beginning."""
    return ["--parameters"] + \
           ["ParameterKey={},ParameterValue={}".format(k, params[k])
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
        subprocess.check_output(cmd)
        return True
    except subprocess.CalledProcessError:
        return False


def create_or_update(verb, template, stack_name, params, quiet, noop):
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


def destroy(stack_name, quiet=False, noop=False):
    cmd = ['aws', 'cloudformation', 'delete-stack',
           "--stack-name", stack_name]
    cmd_str = " ".join(cmd)

    if noop and not quiet:
        print("If noop had not been specified, I would execute this command:")
        print(cmd_str)
    elif not quiet:
        print("I am about to execute this aws command:")
        print(cmd_str)
        print("\nNote that you will have no indication of whether")
        print("the command was successful, but if you want to check")
        print("on it afterwards, run the following command:")
        print("aws cloudformation describe-stacks --stack-name " + stack_name)
    if not noop:
        subprocess.call(cmd)
