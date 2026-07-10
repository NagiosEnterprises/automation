from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r'''
---
module: ncpa_config

short_description: Manage the configuration for the Nagios Cross-Platform Agent (NCPA)

description:
  - Manages the configuration for NCPA

author: "Michael Bellerue (@HunnyPuns)"
attributes:
    check_mode:
        support: none
    diff_mode:
        support: none

options:
    admin_gui_access:
        description:
            - This setting controls whether the admin section is enabled
        default: 1
        type: bool
    admin_password:
        description:
            - If admin panel is available, this option is used to add an extra layer of authentication.
        default: None
        type: str
    admin_only_auth:
        description:
            - Enabling this setting will force NCPA to require admin authentication on GUI login/access. Requires a password set for `admin_password`
        default: 0
        type: bool
    allowed_hosts:
        description:
            - A comma separated list of IP addresses or hostnames of hosts that would be allowed to connect to NCPA
        default: None
        type: str
    allowed_sources:
        description:
            - Allow a host/domain to load the NCPA GUI inside a frame by adding it to X-Frame-Options and Content-Security-Policy frame-ancestors
        default: None
        type: str
    backup_community_string:
        description:
            - An optional backup token that will be used if the primary token does not match
        default: None
        type: str
    certificate:
        description:
            - Allows you to specify the file name for the SSL certificate you wish to use. Using "adhoc" will let NCPA generate its own self-signed certificate.
        default: "adhoc"
        type: str
    check_logging:
        description:
            - Logging of checks run through NCPA
        default: 1
        type: bool
    check_logging_time:
        description:
            - Log retention period, measured in days
        default: 30
        type: int
    community_string:
        description:
            - The token used to authenticate when accessing the API
        default: "mytoken"
        type: str
    connection_timeout:
        description:
            - Connection timeout in seconds that will be used for transmitting the passive check results.
        default: 10
        type: int
    default_units:
        description:
            - Sets the default conversion for bytes (B) to make the metric more readable
        default: "Gi"
        type: str
    delay_start:
        description:
            - Delay the start of the NCPA service by this many seconds
        default: 0
        type: int
    disable_gui:
        description:
            - Disable the web GUI completely while preserving API access
        default: 0
        type: bool
    exclude_fs_types:
        description:
            - A comma separated list of file system types to remove from the 'disk' endpoint
        default: "aufs, autofs, binfmt_misc, cifs, cgroup, configfs, debugfs, devpts, devtmpfs, encryptfs efivarfs, fuse, fusectl, hugetlbfs, mqueue, nfs, overlayfs, proc, pstore, rpc_pipefs, securityfs, selinuxfs, smb, sysfs, tmpfs, tracefs"
        type: str
    gid:
        description:
            - The group that the NCPA service will run as. (Linux/Mac OS X only)
        default: "nagios"
        type: str
    handlers:
        description:
            - Defines what NCPA will do with passive check results
        choices: [none,nrdp]
        default: [none]
    ip:
        description:
            - Sets the IP address that NCPA will listen on
        default: "0.0.0.0"
        type: str
    loglevel:
        description:
            - The level of message to be logged
        choices: [info, error, warning, debug]
        default: [info]
    logfile:
        description:
            - The file location and file name where checks will be stored
        default: "var/log/ncpa_listener.log"
        type: str
    logmaxmb:
        description:
            - The max size allowed for the log file in MB
        default: 5
        type: int
    logbackups:
        description:
            - The number of log rollovers that will be kept
        default: 5
        type: int
    max_connections:
        description:
            - The max number of concurrent connections to the NCPA service, use 0 for unlimited
        default: 200
        type: int
    parent:
        description:
            - The Nagios server's NRDP URL, or next upstream NCPA system
        default: None
        type: str
    port:
        description:
            - Sets the port that NCPA will listen on
        default: 5693
        type: int
    sleep:
        description:
            - The number of seconds NCPA will sleep before running passive checks that do not have their own defined time frame
        default: 300
        type: int
    ssl_ciphers:
        description:
            - Set the list of accepted SSL ciphers in a colon separated format
        type: str
    ssl_version:
        description:
            - Sets the SSL protocol version
        default: "TLSv1_2"
        type: str
    token:
        description:
            - The token used to authenticate against NRDP or upstream NCPA system.
        default: None
        type: str
    uid:
        description:
            - The user that the NCPA service will run as. (Linux/Mac OS X only)
        default: "nagios"
        type: str
'''

def main():

    module = AnsibleModule(
        argument_spec=dict(
            admin_gui_access=dict(type=bool, default=1),
            admin_password=dict(type=str, default="# admin_password ="),
            admin_only_auth=dict(type=bool, default=0),
            allowed_hosts=dict(type=str, default="# allowed_hosts ="),
            allowed_sources=dict(type=str, default="# allowed_sources ="),
            backup_community_string=dict(type=str, default="# backup_community_string ="),
            certificate=dict(type=str, default="# certificate ="),
            check_logging=dict(type=bool, default=1),
            check_logging_time=dict(type=int, default=30),
            community_string=dict(type=str, default="mytoken"),
            connection_timeout=dict(type=int, default=10),
            default_units=dict(type=str, default="Gi"),
            delay_start=dict(type=int, default=0),
            disable_gui=dict(type=bool, default=0),
            exclude_fs_types=dict(type=str, default="aufs, autofs, binfmt_misc, cifs, cgroup, configfs, debugfs, devpts, devtmpfs, encryptfs efivarfs, fuse, fusectl, hugetlbfs, mqueue, nfs, overlayfs, proc, pstore, rpc_pipefs, securityfs, selinuxfs, smb, sysfs, tmpfs, tracefs"),
            gid=dict(type=str, default="nagios"),
            handlers=dict(type=str, default="none", choices=['none','nrdp']),
            ip=dict(type=str, default="0.0.0.0"),
            loglevel=dict(type=str, default="info", choices=['debug, info, warning, error']),
            logfile=dict(type=str, default="var/log/ncpa_listener.log"),
            logmaxmb=dict(type=int, default=5),
            logbackups=dict(type=int, default=5),
            max_connections=dict(type=int, default=200),
            parent=dict(type=str, default="# parent=http://<address>/nrdp"),
            port=dict(type=int, default=5693),
            sleep=dict(type=int, default=300),
            ssl_ciphers=dict(type=str, default="# ssl_ciphers ="),
            ssl_version=dict(type=str, default="TLSv1_2"),
            token=dict(type=str, default="# token ="),
            uid=dict(type=str, default="nagios")
        ),
        supports_check_mode=False
    )

    result = ""
    

if __name__ == "__main__":
    main()
