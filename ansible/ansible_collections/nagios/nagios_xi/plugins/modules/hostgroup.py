#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2026, Chris Story <chris.story@effility.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: hostgroup
short_description: Manage host groups in Nagios XI
description:
  - Create, update, and delete C(hostgroup) objects through the Nagios XI
    REST API (C(config/hostgroup) endpoints of the Core Config Manager).
  - Newly created or modified objects are not active in the monitoring
    engine until the configuration is applied; set I(applyconfig=true)
    or run M(community.nagios_cs.apply_config) once after a batch of changes.
author:
  - Chris Story (@nbkhwjm)
version_added: "1.0.0"
options:
  hostgroup_name:
    description:
      - Short name of the host group.
    type: str
    required: true
  state:
    description:
      - Whether the object should exist.
    type: str
    choices: [present, absent]
    default: present
  applyconfig:
    description:
      - Ask Nagios XI to apply the configuration as part of this request.
      - Applying the configuration restarts the monitoring engine, so for
        bulk changes leave this off and apply once at the end.
    type: bool
    default: false
  properties:
    description:
      - Additional object directives passed straight through to the Core
        Config Manager, using standard Nagios object directive names
        (for example C(alias), C(address), C(check_command),
        C(max_check_attempts), C(contacts), C(members)).
      - List values are encoded as repeated C(key[]) form parameters.
    type: dict
    default: {}
extends_documentation_fragment:
  - community.nagios_cs.nagios_cs
'''

EXAMPLES = r'''
- name: Ensure hostgroup exists
  community.nagios_cs.hostgroup:
    url: https://nagios.example.com
    api_key: "{{ nagios_api_key }}"
    hostgroup_name: my-hostgroup-name
    properties:
      alias: "Linux Servers"
      members: "web01,web02"
- name: Remove hostgroup
  community.nagios_cs.hostgroup:
    url: https://nagios.example.com
    api_key: "{{ nagios_api_key }}"
    hostgroup_name: my-hostgroup-name
    state: absent
    applyconfig: true
'''

RETURN = r'''
changed:
  description: Whether the object was created, updated, or deleted.
  type: bool
  returned: always
object:
  description: The existing Core Config Manager record, when found and unchanged.
  type: dict
  returned: when the object already matched the requested state
api_response:
  description: Raw response returned by the Nagios XI API for write operations.
  type: dict
  returned: on create, update, or delete
'''

from ansible_collections.community.nagios_cs.plugins.module_utils.config_object import (
    run_config_module,
)


def main():
    run_config_module('hostgroup')


if __name__ == '__main__':
    main()
