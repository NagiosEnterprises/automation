#!/usr/bin/python

import platform

def is_ncpa_installed(module):

    rpm_path = module.get_bin_path(
        "rpm"
    )

    if not rpm_path:
        module.fail_json(
            msg="rpm binary not found"
        )

    rc, stdout, stderr = module.run_command(
        [rpm_path, "-q", "ncpa"]
    )

    return rc == 0

def is_nagios_repo_installed(module):

    rpm_path = module.get_bin_path(
        "rpm"
    )

    if not rpm_path:
        module.fail_json(
            msg="rpm binary not found"
        )
    
    rc, stdout, stderr = module.run_command(
        [rpm_path, "-qi", "nagios-repo"]
    )

    return rc == 0

def build_rpm_url(version, major_release, architecture):
    base_url = "https://assets.nagios.com/downloads/ncpa3"

    if version in [None, "", "latest"]:
        filename = f"ncpa-latest-1.{architecture}.rpm"
    else:
        filename = f"ncpa-{version}-1.el{major_release}.{architecture}.rpm"
    
    return f"{base_url}/{filename}"

def parse_os_release():

    os_release = {}

    with open("/etc/os-release", "r") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                os_release[k] = v.strip('"')

    return os_release

def detect_architecture(module):

    arch = platform.machine().lower()

    arch_map = {
        "x86_64": "x86_64",
        "amd64": "x86_64",
        "aarch64": "aarch64",
        "arm64": "aarch64"
    }

    return arch_map.get(arch, arch)

def get_paths(module):
    
    paths = {
        "rpm": module.get_bin_path("rpm"),
        "dnf": module.get_bin_path("dnf")
    }
    
    return paths


def install_rhel_direct(module):
    changed = False

    version = module.params.get("version")
    major_release = parse_os_release()
    architecture = detect_architecture(module)
    paths = get_paths(module)

    if is_ncpa_installed(module):
        return module.fail_json(
            changed=False,
            msg="NCPA already installed"
        )

    if module.check_mode:
        module.exit_json(changed=True)
    
    url = build_rpm_url(
        version,
        major_release["VERSION"],
        architecture
    )

    if not url:
        module.fail_json(
            msg="failed to build url."
        )

    cmd = [
        paths["dnf"],
        "-y",
        "install",
        url
    ]

    rc, stdout, stderr = module.run_command(cmd)

    if rc != 0:
        module.fail_json(
            msg="Failed to install NCPA",
            stderr=stderr
        )

    changed = True

    module.exit_json(
        changed=changed,
        msg="NCPA installed successfully"
    )


def install_rhel_repository(module):
    changed = False

    version = module.params.get("version")
    os_release = parse_os_release()
    architecture = detect_architecture(module)
    paths = get_paths(module)
    repo_dash_map = {
        "8": 2,
        "9": 2,
        "10": 1
    }
    repo_dash_num = repo_dash_map[os_release['VERSION_ID']]

    repo_url = (
        f"https://repo.nagios.com/nagios/"
        f"{os_release['VERSION_ID']}/"
        f"nagios-repo-{os_release['VERSION_ID']}"
        f"-{repo_dash_num}.el{os_release['VERSION_ID']}.noarch.rpm"
    )

    if not is_nagios_repo_installed(module):
            rc, stdout, stderr = module.run_command(
                [paths["rpm"], 
                 "-Uvh", 
                 repo_url]
            )

            if rc != 0:
                module.fail_json(
                    msg="Failed to install the nagios-repo rpm",
                    stderr=stderr
                )

    if is_ncpa_installed(module):
        module.exit_json(
            changed=False,
            msg="NCPA already installed"
        )

    rc, stdout, stderr = module.run_command(
        [paths["dnf"], "install", "-y", "ncpa"]
    )

    if rc != 0:
        module.fail_json(
            msg="Failed to install NCPA",
            stderr=stderr
        )

    rc = ""
    stdout = ""
    stderr = ""

    rc, stdout, stderr = module.run_command(
        ["systemctl", "enable", "ncpa"]
    )

    if rc != 0:
        module.fail_json(
            msg="Failed to set NCPA to start on boot",
            stderr=stderr
        )

    if module.check_mode:
        return module.exit_json(changed=True)