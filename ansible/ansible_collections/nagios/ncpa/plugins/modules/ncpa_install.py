from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nagios.ncpa.plugins.module_utils.ncpa_common import (
   parse_os_release,
   detect_pkg_family
)
from ansible_collections.nagios.ncpa.plugins.module_utils.rhel import (
    handle_rhel
)
from ansible_collections.nagios.ncpa.plugins.module_utils.debian import (
    handle_deb
)

DOCUMENTATION = r'''
---
module: ncpa_install

short_description: Install and manage Nagios Cross Platform Agent (NCPA)

description:
  - Installs and manages NCPA on supported operating systems.
  - Supports Red Hat, CentOS, Oracle Linux, Debian, and Ubuntu.

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
    package_source: package

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

def main():

    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=['present', 'absent']),
            install_method=dict(type='str', default='package', choices=['package']),
            package_source=dict(type='str', default='package', choices=['package', 'repository']),
            version=dict(type='str')
        ),
        supports_check_mode=True
    )

    try:
        host_info = parse_os_release()
    except OSError as e:
        module.fail_json(msg="Unable to read /etc/os-release: {0}".format(e))

    pkg_family = detect_pkg_family(host_info)

    if pkg_family == "debian":
        result = handle_deb(module)
    elif pkg_family == "rhel":
        result = handle_rhel(module)
    else:
        distro = host_info.get("PRETTY_NAME") or host_info.get("ID") or "unknown"
        module.fail_json(
            msg=(
                "Unsupported operating system: {0}. "
                "nagios.ncpa supports Red Hat, CentOS, Oracle Linux, Debian, and Ubuntu."
            ).format(distro)
        )

    module.exit_json(**result)

if __name__ == "__main__":
    main() 