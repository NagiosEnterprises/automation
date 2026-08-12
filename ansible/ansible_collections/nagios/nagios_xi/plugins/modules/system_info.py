#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2026, Chris Story <chris.story@effility.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: system_info
short_description: Retrieve Nagios XI product and version information
description:
  - Calls C(GET system/info) and returns product name, version, and
    related details about the XI installation.
author:
  - Chris Story (@nbkhwjm)
version_added: "1.0.0"
extends_documentation_fragment:
  - community.nagios_cs.nagios_cs
'''

EXAMPLES = r'''
- name: Get XI version info
  community.nagios_cs.system_info:
    url: https://nagios.example.com
    api_key: "{{ nagios_api_key }}"
  register: xi
'''

RETURN = r'''
info:
  description: Parsed response from C(system/info).
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
        info = client.get('system/info')
    except NagiosXIAPIError as exc:
        client.fail(exc)
    module.exit_json(changed=False, info=info)


if __name__ == '__main__':
    main()
