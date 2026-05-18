
from ansible_collections.nagios.ncpa.plugins.module_utils.ncpa_common import (
    detect_os_family,
    build_rpm_url
)

module.exit_json(
    changed=False,
    os_family=detect_os_family(),
    rpm_url=build_rpm_url()
)