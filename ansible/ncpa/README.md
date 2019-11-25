These playbooks and roles are designed to distribute NCPA -- the Nagios Cross Platform Agent -- to devices in your environment, and then automatically register the devices for basic monitoring with Nagios XI.

Users adapt these files to their environments through required setup and optional setup. Required setup involves information that must be configured for the automation to work. Optional setup involves modifying the Nagios XI API calls used to configure monitoring of the devices to customize how devices are monitored.

Once at least the required modifications are made, Tower users can launch the job template, while Ansbile CLI users can run the executable run.sh file.


# Required Setup

There are three pieces of information users must supply: 
1) the IP address or FQDN of the Nagios XI installation
2) an administrative-level Nagios XI API key
3) the NCPA authentication token to configure on the devices and XI


## Security considerations for required setup

An administrative-level Nagios XI API key can be used to modify XI configs programmatically. Indeed, this automation does exactly that. The NCPA authentication token grants access to NCPA functionality on the monitored device. Users may wish to encrypt the API key and NCPA token with either Tower Custom Credential Types or a vault file.


### Fast, less-secure method of required setup

1) Tower: add the items as EXTRA VARIABLES in the Job Template:
```yml
---
xi_ip: '192.168.100.100'
xi_api_key: 'XFbaUsuPi0OU3n0jmVkCAkYl78t2DodBkI0eav3sP8G8CHrXS5vooNNubAPOX3lh'
ncpa_token: 'a_secure_token'
```

2) Ansible CLI: add a vars section above the roles section in ncpa_install_and_register.yml:
```yml
  vars:
    xi_ip: '192.168.100.100'
    xi_api_key: 'XFbaUsuPi0OU3n0jmVkCAkYl78t2DodBkI0eav3sP8G8CHrXS5vooNNubAPOX3lh'
    ncpa_token: 'a_secure_token'
```

### More-secure method of required setup
1) Tower: create credential types and credentials for the xi_api_key and ncpa_token vars 

2) Ansible CLI: add a vars_files and a vars section above the roles section in ncpa_install_and_register.yml:
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

# Optional Setup
This automation auto-registers the inventory as hosts in XI, and also configures predefined service monitoring. Users may like to know that they can add additional custom API calls to the automation, or remove those provided API calls they wish not to use. As a full discussion of the Nagios XI API is out of scope for this document, users are directed to the Help page in the Nagios XI interface, which has API documentation and examples of API calls.