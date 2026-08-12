#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2026, Chris Story <chris.story@effility.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: system_status
short_description: Retrieve Nagios XI subsystem/daemon status
description:
  - Calls C(GET system/status), or C(GET system/statusdetail) when
    I(detailed=true), returning the state of the XI daemons and engine.
author:
  - Chris Story (@nbkhwjm)
version_added: "1.0.0"
options:
  detailed:
    description:
      - Query the C(system/statusdetail) endpoint for extended detail
        instead of the summary C(system/status) endpoint.
    type: bool
    default: false
extends_documentation_fragment:
  - community.nagios_cs.nagios_cs
'''

EXAMPLES = r'''
- name: Check daemon status
  community.nagios_cs.system_status:
    url: https://nagios.example.com
    api_key: "{{ nagios_api_key }}"
    detailed: true
'''

RETURN = r'''
status:
  description: Parsed response from the status endpoint.
  type: dict
  returned: always
'''

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.nagios_cs.plugins.module_utils.nagios_cs import (
    NagiosXIClient,
    NagiosXIAPIError,
    nagios_cs_argument_spec,
)


def main():
    argument_spec = nagios_cs_argument_spec()
    argument_spec.update(detailed=dict(type='bool', default=False))
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)
    client = NagiosXIClient(module)
    endpoint = 'system/statusdetail' if module.params['detailed'] else 'system/status'
    try:
        status = client.get(endpoint)
    except NagiosXIAPIError as exc:
        client.fail(exc)
    module.exit_json(changed=False, status=status)


if __name__ == '__main__':
    main()
