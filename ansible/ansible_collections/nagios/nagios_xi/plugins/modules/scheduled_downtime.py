#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2026, Chris Story <chris.story@effility.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: scheduled_downtime
short_description: Schedule or delete downtime in Nagios XI
description:
  - Uses C(POST system/scheduleddowntime) to schedule downtime for hosts,
    host groups, service groups, or all services on given hosts, and
    C(DELETE system/scheduleddowntime/<id>) to remove an existing entry.
  - To find the internal downtime ID for deletion, query
    M(community.nagios_cs.object_info) with C(resource=downtime).
author:
  - Chris Story (@nbkhwjm)
version_added: "1.0.0"
options:
  state:
    description:
      - C(present) schedules new downtime; C(absent) deletes the downtime
        entry identified by I(downtime_id).
    type: str
    choices: [present, absent]
    default: present
  comment:
    description: Comment attached to the downtime. Required for C(present).
    type: str
  start:
    description: Start time as epoch seconds. Required for C(present).
    type: int
  end:
    description: End time as epoch seconds. Required for C(present).
    type: int
  hosts:
    description: Host names to put into downtime.
    type: list
    elements: str
    default: []
  hostgroups:
    description: Host groups to put into downtime.
    type: list
    elements: str
    default: []
  servicegroups:
    description: Service groups to put into downtime.
    type: list
    elements: str
    default: []
  all_services:
    description: Also schedule downtime for all services on I(hosts).
    type: bool
    default: false
  downtime_id:
    description: Internal downtime ID to delete. Required for C(absent).
    type: int
extends_documentation_fragment:
  - community.nagios_cs.nagios_cs
'''

EXAMPLES = r'''
- name: Schedule a 2 hour maintenance window
  community.nagios_cs.scheduled_downtime:
    url: https://nagios.example.com
    api_key: "{{ nagios_api_key }}"
    comment: Patching window
    start: "{{ now(utc=true).timestamp() | int }}"
    end: "{{ (now(utc=true).timestamp() | int) + 7200 }}"
    hosts:
      - web01
      - web02
    all_services: true

- name: Cancel downtime entry 10
  community.nagios_cs.scheduled_downtime:
    url: https://nagios.example.com
    api_key: "{{ nagios_api_key }}"
    state: absent
    downtime_id: 10
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
        state=dict(type='str', choices=['present', 'absent'],
                   default='present'),
        comment=dict(type='str'),
        start=dict(type='int'),
        end=dict(type='int'),
        hosts=dict(type='list', elements='str', default=[]),
        hostgroups=dict(type='list', elements='str', default=[]),
        servicegroups=dict(type='list', elements='str', default=[]),
        all_services=dict(type='bool', default=False),
        downtime_id=dict(type='int'),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ('state', 'present', ('comment', 'start', 'end')),
            ('state', 'absent', ('downtime_id',)),
        ],
    )
    client = NagiosXIClient(module)
    if module.check_mode:
        module.exit_json(changed=True)
    try:
        if module.params['state'] == 'absent':
            response = client.delete(
                'system/scheduleddowntime/%d' % module.params['downtime_id'])
        else:
            data = dict(
                comment=module.params['comment'],
                start=module.params['start'],
                end=module.params['end'],
            )
            if module.params['hosts']:
                data['hosts'] = module.params['hosts']
            if module.params['hostgroups']:
                data['hostgroups'] = module.params['hostgroups']
            if module.params['servicegroups']:
                data['servicegroups'] = module.params['servicegroups']
            if module.params['all_services']:
                data['all_services'] = 1
            response = client.post('system/scheduleddowntime', data=data)
    except NagiosXIAPIError as exc:
        client.fail(exc)
    module.exit_json(changed=True, api_response=response)


if __name__ == '__main__':
    main()
