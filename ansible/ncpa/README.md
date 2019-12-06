These playbooks and roles are designed to distribute the Nagios Cross Platform Agent (NCPA) to devices in your environment, and then register the devices for monitoring via the Nagios XI API.

Users adapt these files to their environments through required and optional setup.


# Required Setup

Users must supply three pieces of information: 
1) the IP address or FQDN of the Nagios XI installation
2) an administrative-level Nagios XI API key
3) the NCPA authentication token


## Security considerations for required setup

An administrative-level Nagios XI API key can be used to modify any or all XI configs programmatically. The NCPA authentication token grants access to NCPA functionality on the monitored device.


### Fast, less-secure required setup

1) Tower/AWX: add the items as EXTRA VARIABLES in the Job Template:
```yml
---
xi_ip: '192.168.100.100'
xi_api_key: 'XFbaUsuPi0OU3n0jmVkCAkYl78t2DodBkI0eav3sP8G8CHrXS5vooNNubAPOX3lh'
ncpa_token: 'a_secure_token'
```

2) Ansible CLI: add a vars section above the roles section(s) in linux_ncpa_install_and_register.yml and windows_ncpa_install_and_register.yml:
```yml
  vars:
    xi_ip: '192.168.100.100'
    xi_api_key: 'XFbaUsuPi0OU3n0jmVkCAkYl78t2DodBkI0eav3sP8G8CHrXS5vooNNubAPOX3lh'
    ncpa_token: 'a_secure_token'
```

### More secure required setup
1) Tower/AWX: create credential types and credentials for the xi_api_key and ncpa_token vars.

2) Ansible CLI: add a vars_files and a vars section above the roles section(s) in linux_ncpa_install_and_register.yml and windows_ncpa_install_and_register.yml:
```yml
  vars_files:
    - 'secrets.yml'
  vars:
    xi_ip: '192.168.100.100'
```

Set the XI API Key and the NCPA Token in the vault-encrypted secrets.yml file:
Run ansible-vault edit secrets.yml * It may ask you for the password three times, this is a known ansible bug
Enter password hunter2 as this is the example used * Feel free to change this as you see fit
File will look something like this, update to suit your environment:
```yml
---
xi_api_key: 'XFbaUsuPi0OU3n0jmVkCAkYl78t2DodBkI0eav3sP8G8CHrXS5vooNNubAPOX3lh'
ncpa_token: 'DabohKGprhau'
```

When running the playbook, prompt Ansible to prompt the user for the vault password with the --ask-vault-pass flag as in this example:
```
ansible-playbook linux_ncpa_install_and_register.yml --ask-vault-pass
```


# Optional Setup
Several of these roles generate API calls to Nagios XI. You may wish to edit lines the roles to perhaps assign an appropriate contact (for example) or perhaps change a threshold or adjust a notification_interval. You might wish to edit the main playbooks to remove certain roles/API calls, or create new roles/API calls to suit your environment.


### Nagios XI API documentation location
The Nagios XI API is documented in the Help page of the Nagios XI interface.


### Notes on editing, adding, and deleting roles that create API calls
If you exclude the xi_apply_config role in a playbook that makes API calls, XI will still receive the calls, though the changes will not be applied. You would apply the config manually in the XI CCM.

The roles that register services provide the minimum configs (host_name, service_description, check_command, check_interval, retry_interval, max_check_attempts, check_period, contacts, notification_interval, notification_period) required for a valid Nagios service config. If you do not include at least those configs in a service role, the service will not be registered. You can add any additional config variable found here https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/objectdefinitions.html#service . Make sure to follow the existing format exactly. Be alert for issues regarding commas, quotes, and escape characters.

The role that registers hosts provides the minimum configs (host_name, address, max_check_attempts, check_period, contacts, notification_interval, notification_period) required for a valid Nagios host config. If you do not include at least those configs in the host role, the host will not be registered. You can add any additional config variable found here https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/objectdefinitions.html#host . Make sure to follow the existing format exactly. Be alert for issues regarding commas, quotes, and escape characters.