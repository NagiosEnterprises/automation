CONFIG_DEFAULTS = {
    'path' = '/usr/local/ncpa/etc/ncpa.cfg',
    'general' = {
        'check_logging' = 1,
        'check_logging_time' = 30,
        'loglevel' = 'info',
        'logmaxmb' = 5,
        'logbackups' = 5,
        'uid' = 'nagios',
        'gid' = 'nagios',
        'pidfile' = 'var/run/ncpa.pid',
        'all_partitions' = 1,
        'exclude_fs_types' = 'aufs,autofs,binfmt_misc,cifs,cgroup,configfs,debugfs,devpts,devtmpfs,encryptfs,efivarfs,fuse,fusectl,hugetlbfs,mqueue,nfs,overlayfs,proc,pstore,rpc_pipefs,securityfs,selinuxfs,smb,sysfs,tmpfs,tracefs,nfsd,xenfs,squashfs',
        'default_units' = 'Gi'
    },
    'listener' = {
        'ip' = '::',
        'port' = 5693,
        'ssl_version' = 'TLSv1_2',
        'certificate' = 'adhoc',
        'ssl_ciphers' = '',
        'logfile' = 'var/log/ncpa_listener.log',
        'delay_start' = 0,
        'admin_gui_access' = 1,
        'admin_password' = 'None',
        'admin_auth_only' = 0,
        'allowed_hosts' = '',
        'max_connections' = 200,
        'allowed_sources' = '',
        'allow_config_edit' = 1
    },
    'api' = {
        'community_string' = 'mytoken'
    },
    'passive' = {
        'handlers' = 'None',
        'sleep' = 300,
        'logfile' = 'var/log/ncpa_passive.log',
        'delay_start' = 0
    },
    'nrdp' = {
        'parent' = '',
        'token' = '',
        'hostname' = '',
        'connection_timeout' = 10
    },
    'kafkaproducer' = {
        'hostname' = 'None',
        'servers' = 'localhost:9092',
        'clientname' = 'NCPA-Kafka',
        'topic' = 'ncpa'
    },
    'plugin directives' = {
        'plugin_path' = 'plugins/',
        'follow_symlinks' = 0,
        'plugin_timeout' = 59,
        'run_with_sudo' = '',
        'plugin_extensions' = {
            '.sh' = '/bin/sh $plugin_name $plugin_args',
            '.py' = 'python3 $plugin_name $plugin_args',
            '.pl' = 'perl $plugin_name $plugin_args',
            '.php' = 'php $plugin_name $plugin_args',
            '.ps1' = 'powershell -ExecutionPolicy Bypass -File $plugin_name $plugin_args',
            '.vbs' = 'cscript $plugin_name $plugin_args //NoLogo',
            '.wsf' = 'cscript $plugin_name $plugin_args //NoLogo',
            '.bat' = 'cmd /c $plugin_name $plugin_args'
        }
    }
}