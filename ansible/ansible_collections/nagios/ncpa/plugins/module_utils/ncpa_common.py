#!/usr/bin/python

import subprocess


DOCUMENTATION = r'''
---
module: ncpa_install

short_description: Install and manage Nagios Cross Platform Agent (NCPA)

description:
  - Installs and manages NCPA on supported operating systems.

options:

  state:
    description:
      - Desired package state.
    choices: [present, absent]
    default: present
    type: str

  install_method:
    description:
      - Installation method.
    choices: [package]
    default: package
    type: str

  package_source:
    description:
      - Whether to install directly or configure repository.
    choices: [direct, repository]
    default: direct
    type: str

  version:
    description:
      - Specific NCPA version to install.
    type: str

author:
  - Nagios Enterprises
'''

EXAMPLES = r'''
- name: Install NCPA directly
  nagios.ncpa.ncpa_install:
    package_source: direct

- name: Install NCPA from repository
  nagios.ncpa.ncpa_install:
    package_source: repository
'''

RETURN = r'''
changed:
    description: Whether any changes were made
    type: bool
    returned: always
'''


def detect_os_info():
    os_release = {}

    with open("/etc/os-release", "r") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                os_release[k] = v.strip('"')

    return os_release.get("ID", "").lower()


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

def detect_architecture():
    return "x86_64"

def configure_nagios_repository():
    pass


def install_rhel_direct(module):
    changed = False

    version = module.params.get("version")
    major_release = parse_os_release()
    architecture = detect_architecture()

    if is_ncpa_installed(module):
        module.exit_json(
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

    dnf_path = module.get_bin_path( "dnf" )

    if not dnf_path:
        module.fail_json(
            msg="dnf binary not found"
        )

    cmd = [
        dnf_path,
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
    module.fail_json(
        msg="Repository installation not yet implemented"
    )
