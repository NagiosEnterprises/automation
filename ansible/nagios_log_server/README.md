These playbooks and roles are designed to automatically configure log forwarding from the devices and applications in your environment to Nagios Log Server.

Users adapt these files to their environments through required and optional setup.


# Required Setup

Users must supply the IP address or FQDN of the Nagios Log Server installation.

1) Tower/AWX: add the item in EXTRA VARIABLES in the Job Template:
```yml
---
nls_ip: '192.168.100.100'
```

2) Ansible CLI: add a vars section above the roles section(s) in the playbooks:
```yml
  vars:
    nls_ip: '192.168.100.100'
```


# Optional Setup

### Linux syslog
You are welcome to edit which roles are called by the main Linux syslog playbook. If you don't have to contend with selinux or you don't have MySQL logs to monitor, you can remove those roles.


### Windows Eventlog
The Windows Eventlog playbook installs a forwarding agent called NxLog, drops in a configuration file, and starts/restarts the NxLog service. The configuration file is a jinja template. The default template included here handles basic Eventlog forwarding, though the configuration file can be modified to also forward IIS or other logs as well. Please see the documentation for IIS and Windows files forwarding in the Nagios Log Server interface.