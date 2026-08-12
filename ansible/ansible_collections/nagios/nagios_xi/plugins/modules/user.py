#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2026, Chris Story <chris.story@effility.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: user
short_description: Manage Nagios XI web interface users
description:
  - Creates and deletes Nagios XI users through C(POST system/user) and
    C(DELETE system/user).
  - Existing users are detected with C(GET system/user); the API does not
    support in-place updates of every attribute, so this module does not
    modify existing users.
author:
  - Chris Story (@nbkhwjm)
version_added: "1.0.0"
options:
  username:
    description: Login name of the user.
    type: str
    required: true
  state:
    description: Whether the user should exist.
    type: str
    choices: [present, absent]
    default: present
  name:
    description: Full display name. Required when creating a user.
    type: str
  email:
    description: Email address. Required when creating a user.
    type: str
  password:
    description: Initial password. Required when creating a user.
    type: str
  auth_level:
    description: Authorization level for the new user.
    type: str
    choices: [user, admin]
    default: user
  force_pw_change:
    description: Force a password change at first login.
    type: bool
    default: false
  extra:
    description:
      - Additional parameters passed through to C(system/user), such as
        C(phone), C(language), or C(auth_type).
    type: dict
    default: {}
extends_documentation_fragment:
  - community.nagios_cs.nagios_cs
'''

EXAMPLES = r'''
- name: Create an XI user
  community.nagios_cs.user:
    url: https://nagios.example.com
    api_key: "{{ nagios_api_key }}"
    username: jdoe
    name: Jane Doe
    email: jdoe@example.com
    password: "{{ vaulted_password }}"
    auth_level: user
    force_pw_change: true

- name: Remove an XI user
  community.nagios_cs.user:
    url: https://nagios.example.com
    api_key: "{{ nagios_api_key }}"
    username: jdoe
    state: absent
'''

RETURN = r'''
api_response:
  description: Raw response from the API for create/delete operations.
  type: dict
  returned: changed
'''

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.nagios_cs.plugins.module_utils.nagios_cs import (
    NagiosXIClient,
    NagiosXIAPIError,
    nagios_cs_argument_spec,
)


def _user_exists(client, username):
    try:
        result = client.get('system/user')
    except NagiosXIAPIError:
        return None
    records = []
    if isinstance(result, dict):
        for value in result.values():
            if isinstance(value, list):
                records = value
                break
    elif isinstance(result, list):
        records = result
    for record in records:
        if isinstance(record, dict) and record.get('username') == username:
            return record
    return False


def main():
    argument_spec = nagios_cs_argument_spec()
    argument_spec.update(
        username=dict(type='str', required=True),
        state=dict(type='str', choices=['present', 'absent'],
                   default='present'),
        name=dict(type='str'),
        email=dict(type='str'),
        password=dict(type='str', no_log=True),
        auth_level=dict(type='str', choices=['user', 'admin'],
                        default='user'),
        force_pw_change=dict(type='bool', default=False),
        extra=dict(type='dict', default={}),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[('state', 'present', ('name', 'email', 'password'))],
    )
    client = NagiosXIClient(module)
    username = module.params['username']
    state = module.params['state']

    try:
        existing = _user_exists(client, username)

        if state == 'absent':
            if existing is False:
                module.exit_json(changed=False)
            if module.check_mode:
                module.exit_json(changed=True)
            # Newer XI versions delete by numeric user ID; fall back to the
            # legacy username query parameter when no ID can be resolved.
            user_id = None
            if isinstance(existing, dict):
                user_id = existing.get('user_id') or existing.get('id')
            if user_id:
                response = client.delete('system/user/%s' % user_id)
            else:
                response = client.delete('system/user',
                                         params={'username': username})
            module.exit_json(changed=True, api_response=response)

        if existing:
            module.exit_json(changed=False, user=existing)
        if module.check_mode:
            module.exit_json(changed=True)

        payload = dict(module.params['extra'])
        payload.update(
            username=username,
            name=module.params['name'],
            email=module.params['email'],
            password=module.params['password'],
            auth_level=module.params['auth_level'],
            force_pw_change=1 if module.params['force_pw_change'] else 0,
        )
        response = client.post('system/user', data=payload)
    except NagiosXIAPIError as exc:
        client.fail(exc)
    module.exit_json(changed=True, api_response=response)


if __name__ == '__main__':
    main()
