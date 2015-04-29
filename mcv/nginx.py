import subprocess
from jinja2 import Template


def nginx_reload():
    return subprocess.call(["nginx -s reload"], shell=True)


def rollout_servers(template_path, config_path, addrs, listen):
    """Render a set of server addresses into a Jinja2 template,
    copy the output into the configuration path and reload
    running nginx configuration

    Template must expect `addrs` and `listen` variables
      addrs - List of available upstream addresses
      listen - ex: 3000 or '443 ssl'"""
    with open(template_path, "r") as f:
        tmpl = Template(f.read())

    with open(config_path, "w") as f:
        f.write(tmpl.render(addrs=addrs, listen=listen))
    nginx_reload()
