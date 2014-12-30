import subprocess
import distutils.spawn
import os
import re


def _uberjar(project_path):
    lein_cmd = distutils.spawn.find_executable('lein')

    env = os.environ.copy()
    env['LEIN_ROOT'] = 'yes'  # Allow Leiningen to run as root

    p = subprocess.Popen(
        [lein_cmd, "uberjar"],
        cwd=project_path,
        env=env,
        stdout=subprocess.PIPE)
    output, output_err = p.communicate()
    return output


def _file_from_uberjar_output(output):
    r = re.compile("Created (.*-standalone.jar)")
    m = re.search(r, output)
    return file(m.group(1)) if m else None


def uberjar(project_path):
    """Build an uberjar in the context of `project_path`, return the
    file object of the standalone JAR"""
    output = _uberjar(project_path)
    return _file_from_uberjar_output(output)
