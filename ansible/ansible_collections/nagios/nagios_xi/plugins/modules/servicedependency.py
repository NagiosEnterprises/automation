#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2026, Chris Story <chris.story@effility.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: servicedependency
short_description: Manage service dependencies in Nagios XI
description:
  - Create, update, and delete C(servicedependency) objects through the Nagios XI
    REST API (C(config/servicedependency) endpoints of the Core Config Manager).
  - Newly created or modified objects are not active in the monitoring
    engine until the configuration is applied; set I(applyconfig=true)
    or run M(community.nagios_cs.apply_config) once after a batch of changes.
  - Nagios does not enforce uniqueness for this object type, so
    idempotency is best-effort and based on the identifying options
    listed below.
author:
  - Chris Story (@nbkhwjm)
version_added: "1.0.0"
options:
  host_name:
    description:
      - Master host name.
    type: str
    required: true
  service_description:
    description:
      - Master service description.
    type: str
    required: true
  dependent_host_name:
    description:
      - Dependent host name.
    type: str
    required: true
  dependent_service_description:
    description:
      - Dependent service description.
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
- name: Ensure servicedependency exists
  community.nagios_cs.servicedependency:
    url: https://nagios.example.com
    api_key: "{{ nagios_api_key }}"
    host_name: my-host-name
    service_description: my-service-description
    dependent_host_name: my-dependent-host-name
    dependent_service_description: my-dependent-service-description
    properties:
      notification_failure_criteria: "w,u,c"
      execution_failure_criteria: "w,u,c"
- name: Remove servicedependency
  community.nagios_cs.servicedependency:
    url: https://nagios.example.com
    api_key: "{{ nagios_api_key }}"
    host_name: my-host-name
    service_description: my-service-description
    dependent_host_name: my-dependent-host-name
    dependent_service_description: my-dependent-service-description
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
    run_config_module('servicedependency')


if __name__ == '__main__':
    main()
