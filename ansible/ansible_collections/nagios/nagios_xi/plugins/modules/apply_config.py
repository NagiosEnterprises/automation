#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2026, Chris Story <chris.story@effility.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: apply_config
short_description: Apply the Nagios XI monitoring configuration
description:
  - Triggers C(POST system/applyconfig), which writes pending Core Config
    Manager changes to the monitoring engine and restarts it.
  - Always reports C(changed=true) when the apply is submitted, since the
    API does not report whether changes were pending.
author:
  - Chris Story (@nbkhwjm)
version_added: "1.0.0"
extends_documentation_fragment:
  - community.nagios_cs.nagios_cs
'''

EXAMPLES = r'''
- name: Apply configuration after a batch of changes
  community.nagios_cs.apply_config:
    url: https://nagios.example.com
    api_key: "{{ nagios_api_key }}"
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
    module = AnsibleModule(argument_spec=nagios_cs_argument_spec(),
                           supports_check_mode=True)
    client = NagiosXIClient(module)
    if module.check_mode:
        module.exit_json(changed=True)
    try:
        response = client.post('system/applyconfig')
    except NagiosXIAPIError as exc:
        client.fail(exc)
    module.exit_json(changed=True, api_response=response)


if __name__ == '__main__':
    main()
