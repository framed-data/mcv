"""Library for updating sudo rules

This is currently a little janky; it only has the facilities
to filter out old rules from the sudoers file, and add new
rules by templating a rules file.
"""

import re
import os
import mcv.file

sudoers_path = '/etc/sudoers'
sudoers_d_path = '/etc/sudoers.d'


def _comment_out_lines(regex):
    with open(sudoers_path, 'r') as f:
        lines = f.readlines()
        transformed_lines = ["#" + l if regex.match(l) else l for l in lines]
        return ''.join(transformed_lines)


def comment_out(pattern):
    new_rules = _comment_out_lines(re.compile(pattern))
    with open(sudoers_path, 'w') as f:
        f.write(new_rules)


def add_rule_file(rule_file_name, str_content):
    file_path = os.path.join(sudoers_d_path, rule_file_name)
    with open(file_path, 'w') as f:
        f.write(str_content)
    mcv.file.chmod(file_path, 0440)
