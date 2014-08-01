import re

env_file = '/etc/environment'

def parse_environment_file():
    """Return a list of (name, value) tuples representing the env vars in
    /etc/environment."""
    comment = re.compile(r'#.*$')
    assign  = re.compile(r'^(\w+)=(.*)$')
    with open(env_file, 'r') as efile:
        envvars = []
        for line in efile:
            line = comment.sub('', line).strip()
            m = assign.match(line)
            if m: envvars.append(m.groups())
        return envvars

def append_env_setting(name, value):
    """Append the given variable to /etc/environment."""
    with open(env_file, 'a') as efile:
        efile.write("%s=%s\n" % (name, value))

def add_environment_var(name, value):
    """Idempotently add a variable to /etc/environment."""
    env_vars = parse_environment_file()
    var_names = [ var[0] for var in env_vars ]
    if name not in var_names:
        append_env_setting(name, value)