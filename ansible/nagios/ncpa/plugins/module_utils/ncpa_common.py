#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import os
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


def detect_os_family():
    os_release = {}

    with open("/etc/os-release", "r") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                os_release[k] = v.strip('"')

    os_id = os_release.get("ID", "").lower()

    if os_id in ["rhel", "centos", "rocky", "almalinux", "fedora"]:
        return "RedHat"

    if os_id in ["ubuntu", "debian"]:
        return "Debian"

    return "Unknown"


def is_ncpa_installed():
    result = subprocess.run(
        ["rpm", "-q", "ncpa"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return result.returncode == 0


def install_rhel_direct(module):
    changed = False

    if is_ncpa_installed():
        module.exit_json(
            changed=False,
            msg="NCPA already installed"
        )

    if module.check_mode:
        module.exit_json(changed=True)

    url = "https://assets.nagios.com/downloads/ncpa/ncpa-latest.el9.x86_64.rpm"

    cmd = [
        "dnf",
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


def main():

    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=['present', 'absent']),
            install_method=dict(type='str', default='package', choices=['package']),
            package_source=dict(type='str', default='direct', choices=['direct', 'repository']),
            version=dict(type='str')
        ),
        supports_check_mode=True
    )

    os_family = detect_os_family()

    if os_family == "RedHat":

        if module.params["package_source"] == "direct":
            install_rhel_direct(module)

        elif module.params["package_source"] == "repository":
            install_rhel_repository(module)

    module.fail_json(
        msg=f"Unsupported OS family: {os_family}"
    )


if __name__ == "__main__":
    main()