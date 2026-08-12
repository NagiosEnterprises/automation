#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2026, Chris Story <chris.story@effility.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: object_info
short_description: Query the read-only objects section of the Nagios XI API
description:
  - Retrieves status, configuration, and historical data from the
    C(objects/) section of the Nagios XI REST API.
  - Covers every documented objects resource, including host and service
    status, group membership, comments, downtime, log entries, state
    history, notifications, acknowledgements, and performance data export.
author:
  - Chris Story (@nbkhwjm)
version_added: "1.0.0"
options:
  resource:
    description:
      - The objects resource to query.
    type: str
    required: true
    choices:
      - hoststatus
      - servicestatus
      - host
      - service
      - hostgroup
      - hostgroupmembers
      - servicegroup
      - servicegroupmembers
      - contact
      - contactgroup
      - contactgroupmembers
      - timeperiod
      - command
      - comment
      - downtime
      - logentries
      - statehistory
      - notifications
      - acknowledgements
      - rrdexport
      - cpexport
  query:
    description:
      - Optional query-string parameters passed through to the API, used
        for filtering, paging, and ordering.
      - "Examples: C(host_name: web01), C(name: 'lk:web') for a LIKE match,
        C(current_state: 2), C(records: '100:0'), C(orderby: 'host_name:a'),
        C(starttime)/C(endtime) as epoch seconds for historical resources."
    type: dict
    default: {}
extends_documentation_fragment:
  - community.nagios_cs.nagios_cs
'''

EXAMPLES = r'''
- name: Get status of all hosts that are DOWN
  community.nagios_cs.object_info:
    url: https://nagios.example.com
    api_key: "{{ nagios_api_key }}"
    resource: hoststatus
    query:
      current_state: 1
  register: down_hosts

- name: List the first 100 service status records for web01
  community.nagios_cs.object_info:
    url: https://nagios.example.com
    api_key: "{{ nagios_api_key }}"
    resource: servicestatus
    query:
      host_name: web01
      records: "100:0"

- name: Fetch state history for the last day
  community.nagios_cs.object_info:
    url: https://nagios.example.com
    api_key: "{{ nagios_api_key }}"
    resource: statehistory
    query:
      starttime: "{{ (now(utc=true).timestamp() | int) - 86400 }}"
      endtime: "{{ now(utc=true).timestamp() | int }}"
'''

RETURN = r'''
data:
  description: Parsed JSON returned by the API for the requested resource.
  type: dict
  returned: always
'''

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.nagios_cs.plugins.module_utils.nagios_cs import (
    NagiosXIClient,
    NagiosXIAPIError,
    nagios_cs_argument_spec,
)


RESOURCES = ['hoststatus', 'servicestatus', 'host', 'service', 'hostgroup',
             'hostgroupmembers', 'servicegroup', 'servicegroupmembers',
             'contact', 'contactgroup', 'contactgroupmembers', 'timeperiod',
             'command', 'comment', 'downtime', 'logentries', 'statehistory',
             'notifications', 'acknowledgements', 'rrdexport', 'cpexport']


def main():
    argument_spec = nagios_cs_argument_spec()
    argument_spec.update(
        resource=dict(type='str', required=True, choices=RESOURCES),
        query=dict(type='dict', default={}),
    )
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)
    client = NagiosXIClient(module)
    try:
        data = client.get('objects/%s' % module.params['resource'],
                          params=module.params['query'])
    except NagiosXIAPIError as exc:
        client.fail(exc)
    module.exit_json(changed=False, data=data)


if __name__ == '__main__':
    main()
