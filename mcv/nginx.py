import subprocess
from jinja2 import Template


def nginx_reload():
    return subprocess.call(["nginx -s reload"], shell=True)


def rollout_servers(template_path, config_path, opts):
    """Render a set of server addresses into a Jinja2 template,
    copy the output into the configuration path and reload
    running nginx configuration

    opts - Dict of options passed directly to template"""
    with open(template_path, "r") as f:
        tmpl = Template(f.read())

    with open(config_path, "w") as f:
        f.write(tmpl.render(opts=opts))
    nginx_reload()
