#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2026, Chris Story <chris.story@effility.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: auth_token
short_description: Create a short-lived Nagios XI authentication token
description:
  - Calls C(POST system/authtoken) to create a one-time/short-lived login
    token, typically used to build auto-login URLs for the XI interface.
author:
  - Chris Story (@nbkhwjm)
version_added: "1.0.0"
options:
  username:
    description: User the token is created for.
    type: str
    required: true
  valid_min:
    description: Number of minutes the token remains valid.
    type: int
    default: 5
extends_documentation_fragment:
  - community.nagios_cs.nagios_cs
'''

EXAMPLES = r'''
- name: Create a 15-minute auth token for jdoe
  community.nagios_cs.auth_token:
    url: https://nagios.example.com
    api_key: "{{ nagios_api_key }}"
    username: jdoe
    valid_min: 15
  register: token
'''

RETURN = r'''
api_response:
  description: Raw response, including the generated token.
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
        username=dict(type='str', required=True),
        valid_min=dict(type='int', default=5),
    )
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=False)
    client = NagiosXIClient(module)
    try:
        response = client.post('system/authtoken', data=dict(
            username=module.params['username'],
            valid_min=module.params['valid_min'],
        ))
    except NagiosXIAPIError as exc:
        client.fail(exc)
    module.exit_json(changed=True, api_response=response)


if __name__ == '__main__':
    main()
