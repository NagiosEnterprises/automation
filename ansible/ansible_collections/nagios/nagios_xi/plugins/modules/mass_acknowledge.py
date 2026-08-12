#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2026, Chris Story <chris.story@effility.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: mass_acknowledge
short_description: Acknowledge problems in bulk via Nagios XI
description:
  - Calls C(POST system/massacknowledge) to acknowledge current problems
    on hosts and/or services in a single request.
author:
  - Chris Story (@nbkhwjm)
version_added: "1.0.0"
options:
  comment:
    description: Comment recorded with the acknowledgement.
    type: str
    default: Acknowledged by Ansible
  hosts:
    description: Host names whose problems should be acknowledged.
    type: list
    elements: str
    default: []
  services:
    description:
      - Services to acknowledge, each written as
        C(<host_name>!<service_description>).
    type: list
    elements: str
    default: []
  sticky:
    description: Keep the acknowledgement until the object recovers.
    type: bool
    default: true
  notify:
    description: Send an acknowledgement notification to contacts.
    type: bool
    default: false
  persistent:
    description: Keep the comment after the acknowledgement is removed.
    type: bool
    default: false
extends_documentation_fragment:
  - community.nagios_cs.nagios_cs
'''

EXAMPLES = r'''
- name: Acknowledge everything broken on two hosts
  community.nagios_cs.mass_acknowledge:
    url: https://nagios.example.com
    api_key: "{{ nagios_api_key }}"
    comment: Known issue, ticket OPS-1234
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
        comment=dict(type='str', default='Acknowledged by Ansible'),
        hosts=dict(type='list', elements='str', default=[]),
        services=dict(type='list', elements='str', default=[]),
        sticky=dict(type='bool', default=True),
        notify=dict(type='bool', default=False),
        persistent=dict(type='bool', default=False),
    )
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)
    if not module.params['hosts'] and not module.params['services']:
        module.fail_json(msg='At least one of hosts or services is required')
    client = NagiosXIClient(module)
    if module.check_mode:
        module.exit_json(changed=True)
    data = dict(
        comment=module.params['comment'],
        sticky=1 if module.params['sticky'] else 0,
        notify=1 if module.params['notify'] else 0,
        persistent=1 if module.params['persistent'] else 0,
    )
    if module.params['hosts']:
        data['hosts'] = module.params['hosts']
    if module.params['services']:
        data['services'] = module.params['services']
    try:
        response = client.post('system/massacknowledge', data=data)
    except NagiosXIAPIError as exc:
        client.fail(exc)
    module.exit_json(changed=True, api_response=response)


if __name__ == '__main__':
    main()
