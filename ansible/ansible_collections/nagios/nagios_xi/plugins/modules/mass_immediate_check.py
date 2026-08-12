#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2026, Chris Story <chris.story@effility.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: mass_immediate_check
short_description: Schedule immediate checks in bulk via Nagios XI
description:
  - Calls C(POST system/massimmediatecheck) to schedule an immediate
    check of the given hosts and/or services.
author:
  - Chris Story (@nbkhwjm)
version_added: "1.0.0"
options:
  hosts:
    description: Host names to check immediately.
    type: list
    elements: str
    default: []
  services:
    description:
      - Services to check immediately, each written as
        C(<host_name>!<service_description>).
    type: list
    elements: str
    default: []
extends_documentation_fragment:
  - community.nagios_cs.nagios_cs
'''

EXAMPLES = r'''
- name: Recheck web tier now
  community.nagios_cs.mass_immediate_check:
    url: https://nagios.example.com
    api_key: "{{ nagios_api_key }}"
    hosts:
      - web01
      - web02
    services:
      - "web01!HTTP"
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
    argument_spec.update(
        hosts=dict(type='list', elements='str', default=[]),
        services=dict(type='list', elements='str', default=[]),
    )
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)
    if not module.params['hosts'] and not module.params['services']:
        module.fail_json(msg='At least one of hosts or services is required')
    client = NagiosXIClient(module)
    if module.check_mode:
        module.exit_json(changed=True)
    data = {}
    if module.params['hosts']:
        data['hosts'] = module.params['hosts']
    if module.params['services']:
        data['services'] = module.params['services']
    try:
        response = client.post('system/massimmediatecheck', data=data)
    except NagiosXIAPIError as exc:
        client.fail(exc)
    module.exit_json(changed=True, api_response=response)


if __name__ == '__main__':
    main()
