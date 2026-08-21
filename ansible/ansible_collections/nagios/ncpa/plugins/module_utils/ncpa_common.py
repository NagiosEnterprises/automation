#!/usr/bin/python

from platform import machine
from os import path
from os.path import exists as path_exists
from urllib.request import urlretrieve
from requests import get

DEBIAN_IDS = {"debian", "ubuntu"}
RHEL_IDS = {"rhel", "centos", "ol", "oracle", "rocky", "almalinux", "fedora"}
RHEL_ID_LIKE = {"rhel", "centos", "fedora"}

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

def parse_id_like(value):
    if not value:
        return []
    return [os_id.lower() for os_id in value.replace(",", " ").split() if os_id]

def detect_pkg_family(os_release=None):
    """Return 'debian', 'rhel', or 'unsupported' from /etc/os-release."""
    if os_release is None:
        os_release = parse_os_release()

    distro_id = os_release.get("ID", "").lower().strip()
    id_like = parse_id_like(os_release.get("ID_LIKE", ""))

    if distro_id in DEBIAN_IDS or "debian" in id_like:
        return "debian"
    if distro_id in RHEL_IDS or any(os_id in RHEL_ID_LIKE for os_id in id_like):
        return "rhel"
    return "unsupported"

def get_os_major_version(os_release=None):
    """Return the major version from VERSION_ID (e.g. '9.4' -> '9')."""
    if os_release is None:
        os_release = parse_os_release()

    version_id = os_release.get("VERSION_ID", "").strip()
    if not version_id:
        return ""
    return version_id.split(".")[0]

def download_file(url, dest):
    urlretrieve(url, dest)

def detect_architecture(module):

    arch = machine().lower()

    arch_map = {
        "x86_64": "x86_64",
        "amd64": "x86_64",
        "aarch64": "aarch64",
        "arm64": "aarch64"
    }

    return arch_map.get(arch, arch)

def is_nagios_repo_installed(module, paths):
    if isinstance(paths, dict) and paths.get("rpm"):
        rc, stdout, stderr = module.run_command(
            [paths["rpm"], "-q", "nagios-repo"]
        )
        return rc == 0

    if isinstance(paths, dict) and "apt" in paths:
        return (
            path_exists("/etc/apt/sources.list.d/nagios.sources")
            or path_exists("/etc/apt/sources.list.d/nagios.list")
        )

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