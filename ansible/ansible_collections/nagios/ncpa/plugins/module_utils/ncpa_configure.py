from copy import deepcopy
from ansible_collections.nagios.ncpa.plugins.module_utils.ncpa_defaults import (
    CONFIG_DEFAULTS
)
from pathlib import Path
import tempfile
import os


def build_config(user_config):
    config = deepcopy(CONFIG_DEFAULTS)

    if user_config:
        config.update(user_config)
    
    return config

def render_config(module, config_changes):
    lines = []

    lines.append("#")
    lines.append("# This file is managed by Ansible")
    lines.append("# Manual changes will be overwritten")
    lines.append("#")

    lines.append("")

    return "\n".join(lines)

def ensure_file(module, filename, desired_state):

    path = Path(filename)

    if path.exists():
        current = path.read_text(encoding="utf-8")
    else:
        current = ""
    
    if current == desired:
        return False
    
    if module.check_mode:
        return True
    
    fd, tmp = tempfile.mkstemp(dir=path.parent)

    with os.fdopen(fd, "w", encoding="utf-8") as fp:
        fp.write(desired_state)
    
    os.replace(tmp, path)

    return True