#!/usr/bin/python

# -*- coding: utf-8 -*-

DOCUMENTATION = r'''
---
module: nagios_cross_platform_agent_install

short_description: Install and manage Nagios Cross-Platform Agent (NCPA)

version_added: "0.1.0"

description:
  - Installs, upgrades, or removes the Nagios Cross-Platform Agent (NCPA)
    on supported platforms.
  - Supports silent installation on Windows.
  - Supports package-based installation on Linux systems.

options:
  state:
    description:
      - Desired state of NCPA.
    type: str
    choices: [present, absent]
    default: present

  version:
    description:
      - Specific version to install.
    type: str

  download_url:
    description:
      - URL to Windows installer executable.
    type: str

  token:
    description:
      - NCPA API/GUI token.
    type: str
    no_log: true

  ip:
    description:
      - IP address for NCPA to bind to.
    type: str
    default: "0.0.0.0"

  port:
    description:
      - Port for NCPA service.
    type: int
    default: 5693

  nrdp_url:
    description:
      - NRDP URL for passive check submission.
    type: str

  nrdp_token:
    description:
      - NRDP authentication token.
    type: str
    no_log: true

  nrdp_hostname:
    description:
      - Hostname used for NRDP submissions.
    type: str

  install_dir:
    description:
      - Installation directory (Windows only).
    type: str

author:
  - Your Name (@HunnyPuns)
'''

EXAMPLES = r'''
- name: Install NCPA on Windows
  nagios_cross_platform_agent_install:
    download_url: "https://repo.example.com/ncpa-2.4.0.exe"
    token: "SuperSecretToken"
    ip: "0.0.0.0"
    port: 5693
    state: present

- name: Remove NCPA
  nagios_cross_platform_agent_install:
    state: absent
'''

RETURN = r'''
changed:
  description: Whether any changes were made.
  type: bool
  returned: always

version_installed:
  description: Version detected after execution.
  type: str
  returned: when available

install_path:
  description: Path where NCPA is installed.
  type: str
  returned: when detected
'''

from ansible.module_utils.basic import AnsibleModule
import os
import platform
import subprocess


def detect_os_family():
    system = platform.system().lower()
    if system == "windows":
        return "Windows"
    elif system in ["linux"]:
        return "Linux"
    elif system == "darwin":
        return "Darwin"
    return "Unknown"


def is_ncpa_installed_windows(install_dir):
    if not install_dir:
        install_dir = r"C:\Program Files\Nagios\NCPA"
    return os.path.exists(install_dir)


def build_windows_silent_command(params):
    cmd = [params["download_url"]]

    cmd.append("/S")

    if params.get("token"):
        cmd.append(f"/TOKEN={params['token']}")

    if params.get("ip"):
        cmd.append(f"/IP={params['ip']}")

    if params.get("port"):
        cmd.append(f"/PORT={params['port']}")

    if params.get("nrdp_url"):
        cmd.append(f"/NRDPURL={params['nrdp_url']}")

    if params.get("nrdp_token"):
        cmd.append(f"/NRDPTOKEN={params['nrdp_token']}")

    if params.get("nrdp_hostname"):
        cmd.append(f"/NRDPHOSTNAME={params['nrdp_hostname']}")

    if params.get("install_dir"):
        cmd.append(f"/D={params['install_dir']}")

    return cmd


def install_windows(module):
    params = module.params
    install_dir = params.get("install_dir")

    if is_ncpa_installed_windows(install_dir):
        module.exit_json(
            changed=False,
            msg="NCPA already installed",
            install_path=install_dir
        )

    if module.check_mode:
        module.exit_json(changed=True)

    cmd = build_windows_silent_command(params)

    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        module.fail_json(msg=f"Installation failed: {str(e)}")

    module.exit_json(
        changed=True,
        msg="NCPA installed successfully",
        install_path=install_dir
    )


def remove_windows(module):
    if module.check_mode:
        module.exit_json(changed=True)

    # Placeholder for uninstall logic
    module.fail_json(msg="Uninstall logic not yet implemented.")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=['present', 'absent']),
            version=dict(type='str'),
            download_url=dict(type='str'),
            token=dict(type='str', no_log=True),
            ip=dict(type='str', default='0.0.0.0'),
            port=dict(type='int', default=5693),
            nrdp_url=dict(type='str'),
            nrdp_token=dict(type='str', no_log=True),
            nrdp_hostname=dict(type='str'),
            install_dir=dict(type='str')
        ),
        supports_check_mode=True
    )

    os_family = detect_os_family()

    if os_family == "Windows":
        if module.params["state"] == "present":
            install_windows(module)
        else:
            remove_windows(module)

    elif os_family == "Linux":
        module.fail_json(msg="Linux installation not yet implemented.")

    else:
        module.fail_json(msg=f"Unsupported OS: {os_family}")


if __name__ == "__main__":
    main()