#!/usr/bin/python

from platform import machine
from os import path
from requests import get

def is_ncpa_installed(module,path):
    rc = False

    if path == "rpm":
        rc = module.run_command(
            [path["rpm"], "-q", "ncpa"]
        )
    elif path == "apt":
        rc = module.run_command(
            [path["apt"], "-q", "ncpa"]
        )
    
    if rc == 0:
        return False
    else:
        return True

def parse_os_release():

    os_release = {}

    with open("/etc/os-release", "r") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                os_release[k] = v.strip('"')

    return os_release

def detect_architecture(module):

    arch = machine().lower()

    arch_map = {
        "x86_64": "x86_64",
        "amd64": "x86_64",
        "aarch64": "aarch64",
        "arm64": "aarch64"
    }

    return arch_map.get(arch, arch)

def is_nagios_repo_installed(module,path):
    if "rpm" in path:
        rc, stdout, stderr = module.run_command(
            ["ls", "/etc/yum.repolist.d/nagios*"]
        )

        if rc == 0:
            return True
        else:
            return False
    
    elif "apt" in path:
        rc, stdout, stderr = module.run_command(
            ["ls", "/etc/apt/sources.list.d/nagios*"]
        )

        if rc == 0:
            return True
        else:
            return False
    
def get_install_ncpa_version(module,path):
    return {
        "changed": False,
        "msg": f"ERROR: get_install_ncpa_version() not implemented yet."
    }

def ensure_file(module,file_path,desired_content):
    current = None

    if path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            current = f.read()
    
    if current == desired_content:
        return False
    if not module.check_mode :
        rc = module.run_command(
            ["rm", "-f", file_path]
        )
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(desired_content)
        
        return True
    
def get_gpg_keys():
    gpg_keys = {}
    gpg_keys["v2"] = get("https://repo.nagios.com/GPG-KEY-NAGIOS-V2").text.strip('\n')
    gpg_keys["v3"] = get("https://repo.nagios.com/GPG-KEY-NAGIOS-V3").text.strip('\n')

    return gpg_keys