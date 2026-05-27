
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nagios.ncpa.plugins.module_utils.ncpa_common import (
    install_rhel_direct,
    install_rhel_repository
)

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

    result = ""
    if module.params.get("package_source") == "repository":
        result = install_rhel_repository(module)
    else:
        result = install_rhel_direct(module)
    
    module.exit_json(**result)

if __name__ == "__main__":
    main()