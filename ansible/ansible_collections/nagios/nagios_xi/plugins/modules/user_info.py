#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2026, Chris Story <chris.story@effility.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: user_info
short_description: List Nagios XI web interface users
description:
  - Retrieves the list of XI users via C(GET system/user).
author:
  - Chris Story (@nbkhwjm)
version_added: "1.0.0"
extends_documentation_fragment:
  - community.nagios_cs.nagios_cs
'''

EXAMPLES = r'''
- name: List all XI users
  community.nagios_cs.user_info:
    url: https://nagios.example.com
    api_key: "{{ nagios_api_key }}"
  register: users
'''

RETURN = r'''
users:
  description: Parsed response from C(system/user).
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
    module = AnsibleModule(argument_spec=nagios_cs_argument_spec(),
                           supports_check_mode=True)
    client = NagiosXIClient(module)
    try:
        users = client.get('system/user')
    except NagiosXIAPIError as exc:
        client.fail(exc)
    module.exit_json(changed=False, users=users)


if __name__ == '__main__':
    main()
