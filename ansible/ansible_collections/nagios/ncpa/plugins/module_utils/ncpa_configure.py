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

def render_config(config_changes):
    lines = []

    lines.append("#")
    lines.append("# This file is managed by Ansible")
    lines.append("# Manual changes will be overwritten")
    lines.append("#")

    lines.append("")

    for key in config_changes.items():
        if key[0] != "path":

            if config_changes[key] is dict():
                lines.append("It's a DICT!")
            else:
                lines.append("It's not a dict.")    
                
            
            #lines.append("{0}: {1}".format(str(key[0]),str(config_changes[key[0]])))
            #lines.append("{0}: {1}".format(str(key[0]),str(config_changes[key[0]])))
        
        #lines.append(str(value))
        
        #if value == dict:
        #    lines.append("Value == Dict")
        #else:
            #lines.append("Value != Dict")
        #    lines.append(str(type(value)))
        
        #lines.append("{0}: {1}".format(key,value))
            
        #else:
            #Pass if it's path
        #    pass

    return "\n".join(lines)

def ensure_file(module, filename, desired_state):

    path = Path(filename)

    if path.exists():
        current = path.read_text(encoding="utf-8")
    else:
        current = ""
    
    if current == desired_state:
        return False
    
    if module.check_mode:
        return True
    
    fd, tmp = tempfile.mkstemp(dir=path.parent)

    with os.fdopen(fd, "w", encoding="utf-8") as fp:
        fp.write(desired_state)
    
    os.replace(tmp, path)

    return True