
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nagios.ncpa.plugins.module_utils.ncpa_common import (
    install_rhel_direct
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

    result = install_rhel_direct(module)

    module.exit_json(**result)

if __name__ == "__main__":
    main()