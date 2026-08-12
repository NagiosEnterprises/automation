#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2026, Chris Story <chris.story@effility.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: core_command
short_description: Submit a raw external command to the Nagios Core engine
description:
  - Calls C(POST system/corecommand) to submit any Nagios Core external
    command (the same commands accepted by the engine command pipe).
  - This gives access to every engine action not covered by a dedicated
    module, such as enabling/disabling notifications, scheduling forced
    checks, or submitting passive check results.
author:
  - Chris Story (@nbkhwjm)
version_added: "1.0.0"
options:
  command:
    description:
      - The external command string, without the leading bracketed
        timestamp (Nagios XI adds it).
      - "Example: C(SCHEDULE_FORCED_HOST_CHECK;web01;1741116177) or
        C(DISABLE_NOTIFICATIONS)."
    type: str
    required: true
extends_documentation_fragment:
  - community.nagios_cs.nagios_cs
'''

EXAMPLES = r'''
- name: Globally disable notifications
  community.nagios_cs.core_command:
    url: https://nagios.example.com
    api_key: "{{ nagios_api_key }}"
    command: DISABLE_NOTIFICATIONS

- name: Force an immediate host check
  community.nagios_cs.core_command:
    url: https://nagios.example.com
    api_key: "{{ nagios_api_key }}"
    command: "SCHEDULE_FORCED_HOST_CHECK;web01;{{ now(utc=true).timestamp() | int }}"
'''

RETURN = r'''
api_response:
  description: Raw response from the API.
  type: dict
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.nagios_cs.plugins.module_utils.nagios_cs import (
    NagiosXIClient,
    NagiosXIAPIError,
    nagios_cs_argument_spec,
)


def main():
    argument_spec = nagios_cs_argument_spec()
    argument_spec.update(command=dict(type='str', required=True))
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)
    client = NagiosXIClient(module)
    if module.check_mode:
        module.exit_json(changed=True)
    try:
        response = client.post('system/corecommand',
                               data={'cmd': module.params['command']})
    except NagiosXIAPIError as exc:
        client.fail(exc)
    module.exit_json(changed=True, api_response=response)


if __name__ == '__main__':
    main()
