# -*- coding: utf-8 -*-

# Copyright (c) 2026, Chris Story <chris.story@effility.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_text

from ansible_collections.community.nagios_cs.plugins.module_utils.nagios_cs import (
    NagiosXIClient,
    NagiosXIAPIError,
    nagios_cs_argument_spec,
)

# Definition of every object type exposed by the XI Core Config Manager API.
#   endpoint      -> path under api/v1/
#   id_fields     -> parameters that uniquely identify one object
#   delete_style  -> 'path'  : DELETE config/<type>/<id1>[/<id2>]
#                    'query' : DELETE config/<type>?field=value&...
#   unique        -> whether id_fields are guaranteed unique in CCM
CONFIG_OBJECT_TYPES = {
    'host': dict(endpoint='config/host',
                 id_fields=['host_name'], delete_style='path', unique=True),
    'service': dict(endpoint='config/service',
                    id_fields=['host_name', 'service_description'],
                    delete_style='path', unique=True),
    'hostgroup': dict(endpoint='config/hostgroup',
                      id_fields=['hostgroup_name'], delete_style='path',
                      unique=True),
    'servicegroup': dict(endpoint='config/servicegroup',
                         id_fields=['servicegroup_name'],
                         delete_style='path', unique=True),
    'contact': dict(endpoint='config/contact',
                    id_fields=['contact_name'], delete_style='path',
                    unique=True),
    'contactgroup': dict(endpoint='config/contactgroup',
                         id_fields=['contactgroup_name'],
                         delete_style='path', unique=True),
    'timeperiod': dict(endpoint='config/timeperiod',
                       id_fields=['timeperiod_name'], delete_style='path',
                       unique=True),
    'command': dict(endpoint='config/command',
                    id_fields=['command_name'], delete_style='path',
                    unique=True),
    'hostescalation': dict(endpoint='config/hostescalation',
                           id_fields=['host_name'], delete_style='query',
                           unique=False),
    'serviceescalation': dict(endpoint='config/serviceescalation',
                              id_fields=['host_name', 'service_description'],
                              delete_style='query', unique=False),
    'hostdependency': dict(endpoint='config/hostdependency',
                           id_fields=['host_name', 'dependent_host_name'],
                           delete_style='query', unique=False),
    'servicedependency': dict(endpoint='config/servicedependency',
                              id_fields=['host_name',
                                         'service_description',
                                         'dependent_host_name',
                                         'dependent_service_description'],
                              delete_style='query', unique=False),
}


def _find_existing(client, meta, identity):
    """Return the first CCM record matching the identity fields, or None."""
    try:
        result = client.get(meta['endpoint'], params=identity)
    except NagiosXIAPIError:
        # Some XI versions do not support GET filtering on every type.
        return None

    records = result
    if isinstance(result, dict):
        # Responses are usually {"<type>": [ {...}, ... ]} or {"records": n, ...}
        for value in result.values():
            if isinstance(value, list):
                records = value
                break
        else:
            records = []
    if not isinstance(records, list):
        return None

    for record in records:
        if not isinstance(record, dict):
            continue
        if _record_matches(record, identity):
            return record
    return None


def _record_matches(record, identity):
    """Compare identity fields; CCM returns some fields (e.g. a service's
    host_name) as lists, so membership counts as a match."""
    for field, want in identity.items():
        have = record.get(field)
        if isinstance(have, (list, tuple)):
            if to_text(want) not in [to_text(v) for v in have]:
                return False
        elif to_text(have if have is not None else '') != to_text(want):
            return False
    return True


def _needs_update(existing, properties):
    """Compare desired properties against the current CCM record."""
    for key, desired in properties.items():
        current = existing.get(key)
        if isinstance(desired, (list, tuple)):
            desired_cmp = sorted(to_text(v) for v in desired)
            if isinstance(current, (list, tuple)):
                current_cmp = sorted(to_text(v) for v in current)
            else:
                current_cmp = sorted(
                    v.strip() for v in to_text(current or '').split(',') if v.strip())
            if desired_cmp != current_cmp:
                return True
        else:
            if isinstance(desired, bool):
                desired = 1 if desired else 0
            if to_text(current if current is not None else '') != to_text(desired):
                return True
    return False


def run_config_module(object_type):
    meta = CONFIG_OBJECT_TYPES[object_type]

    argument_spec = nagios_cs_argument_spec()
    argument_spec.update(
        state=dict(type='str', choices=['present', 'absent'],
                   default='present'),
        applyconfig=dict(type='bool', default=False),
        properties=dict(type='dict', default={}),
    )
    for field in meta['id_fields']:
        argument_spec[field] = dict(type='str', required=True)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    client = NagiosXIClient(module)
    state = module.params['state']
    applyconfig = module.params['applyconfig']
    identity = dict((f, module.params[f]) for f in meta['id_fields'])
    properties = module.params['properties'] or {}

    result = dict(changed=False, object_type=object_type, **identity)

    try:
        existing = _find_existing(client, meta, identity)

        if state == 'absent':
            if existing is None and meta['unique']:
                module.exit_json(**result)
            result['changed'] = True
            if module.check_mode:
                module.exit_json(**result)
            params = {}
            if applyconfig:
                params['applyconfig'] = 1
            if meta['delete_style'] == 'path':
                endpoint = meta['endpoint'] + '/' + '/'.join(
                    module.params[f] for f in meta['id_fields'])
                response = client.delete(endpoint, params=params)
            else:
                params.update(identity)
                response = client.delete(meta['endpoint'], params=params)
            result['api_response'] = response
            module.exit_json(**result)

        # state == present
        payload = dict(identity)
        payload.update(properties)
        if applyconfig:
            payload['applyconfig'] = 1

        if existing is None:
            result['changed'] = True
            if module.check_mode:
                module.exit_json(**result)
            response = client.post(meta['endpoint'], data=payload)
            result['api_response'] = response
            module.exit_json(**result)

        # object exists -> update only if something differs
        if not properties or not _needs_update(existing, properties):
            result['object'] = existing
            module.exit_json(**result)

        result['changed'] = True
        if module.check_mode:
            module.exit_json(**result)
        update_payload = dict(properties)
        if applyconfig:
            update_payload['applyconfig'] = 1
        endpoint = meta['endpoint'] + '/' + '/'.join(
            module.params[f] for f in meta['id_fields'])
        response = client.put(endpoint, data=update_payload)
        result['api_response'] = response
        module.exit_json(**result)

    except NagiosXIAPIError as exc:
        client.fail(exc, **result)
