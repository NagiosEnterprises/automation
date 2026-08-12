# -*- coding: utf-8 -*-

# Copyright (c) 2026, Chris Story <chris.story@effility.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json

from ansible.module_utils.urls import fetch_url
from ansible.module_utils.common.text.converters import to_native, to_text
from ansible.module_utils.six.moves.urllib.parse import urlencode, quote


def nagios_cs_argument_spec():
    """Argument spec shared by every module in this collection."""
    return dict(
        url=dict(type='str', required=True),
        api_key=dict(type='str', required=True, no_log=True),
        validate_certs=dict(type='bool', default=True),
        timeout=dict(type='int', default=30),
    )


class NagiosXIAPIError(Exception):
    pass


class NagiosXIClient(object):
    """Thin wrapper around fetch_url for the Nagios XI REST API.

    The XI API authenticates with an ``apikey`` query-string parameter and
    expects request bodies as ``application/x-www-form-urlencoded`` data.
    List values are encoded PHP-style as repeated ``key[]`` parameters
    (e.g. ``hosts[]=web01&hosts[]=web02``).
    """

    def __init__(self, module):
        self.module = module
        base = module.params['url'].rstrip('/')
        # Accept either https://host/nagiosxi or a bare https://host
        if not base.endswith('/nagiosxi'):
            base = base + '/nagiosxi'
        self.base_url = base
        self.api_key = module.params['api_key']
        self.timeout = module.params['timeout']

    # ------------------------------------------------------------------ #
    # encoding helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def encode_pairs(data):
        """Flatten a dict into (key, value) pairs, PHP-array style."""
        pairs = []
        for key, value in (data or {}).items():
            if value is None:
                continue
            if isinstance(value, bool):
                value = 1 if value else 0
            if isinstance(value, (list, tuple)):
                for item in value:
                    pairs.append(('%s[]' % key, to_text(item)))
            elif isinstance(value, dict):
                # nested dicts -> key[subkey]=value (used by some endpoints)
                for sub, sub_val in value.items():
                    pairs.append(('%s[%s]' % (key, sub), to_text(sub_val)))
            else:
                pairs.append((key, to_text(value)))
        return pairs

    def build_url(self, endpoint, params=None):
        query = [('apikey', self.api_key)]
        query.extend(self.encode_pairs(params))
        path = '/'.join(quote(to_text(part), safe='')
                        for part in endpoint.strip('/').split('/'))
        return '%s/api/v1/%s?%s' % (self.base_url, path, urlencode(query))

    # ------------------------------------------------------------------ #
    # request primitives
    # ------------------------------------------------------------------ #
    def request(self, method, endpoint, params=None, data=None):
        url = self.build_url(endpoint, params=params)
        body = None
        headers = {}
        if data:
            body = urlencode(self.encode_pairs(data))
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

        response, info = fetch_url(self.module, url, data=body,
                                   headers=headers, method=method,
                                   timeout=self.timeout)

        status = info.get('status', -1)
        raw = b''
        if response is not None:
            raw = response.read()
        elif info.get('body'):
            raw = info['body']

        text = to_text(raw, errors='surrogate_or_strict').strip()

        if status == -1 or status >= 500:
            raise NagiosXIAPIError(
                'HTTP %s calling %s %s: %s'
                % (status, method, endpoint, info.get('msg', text)))

        if not text:
            payload = {}
        else:
            try:
                payload = json.loads(text)
            except ValueError:
                # Policy: API anomalies are surfaced for reporting to Nagios,
                # never silently worked around. If a JSON payload is embedded
                # in non-JSON noise (e.g. leaked PHP print_r debug output),
                # fail with a report-ready diagnostic instead of using it.
                embedded = self._extract_embedded_json(text)
                if embedded is not None:
                    raise NagiosXIAPIError(
                        'NAGIOS XI API ANOMALY: %s %s (HTTP %s) returned '
                        'non-JSON output around its JSON payload - most '
                        'likely PHP debug output leaked by the endpoint. '
                        'Report this to Nagios. Embedded payload: %s | '
                        'Raw response (first 500 chars): %s'
                        % (method, endpoint, status,
                           json.dumps(embedded)[:300], text[:500]))
                raise NagiosXIAPIError(
                    'Non-JSON response from %s %s (HTTP %s): %s'
                    % (method, endpoint, status, text[:500]))

        # The XI API signals failures with {"error": "..."} even on HTTP 200
        if isinstance(payload, dict) and payload.get('error'):
            raise NagiosXIAPIError(to_native(payload['error']))
        if status >= 400:
            raise NagiosXIAPIError(
                'HTTP %s calling %s %s: %s' % (status, method, endpoint, text[:500]))
        return payload

    @staticmethod
    def _extract_embedded_json(text):
        """Diagnostics-only: find a JSON document embedded in noisy output.

        Used solely to build a report-ready error message when an endpoint
        emits non-JSON output (e.g. PHP print_r debug leaks) around its JSON
        payload. The result is never used as the response - such responses
        are treated as Nagios XI API anomalies and raised to the caller.
        """
        decoder = json.JSONDecoder()
        last = None
        idx = 0
        while idx < len(text):
            starts = [s for s in (text.find('{', idx), text.find('[', idx))
                      if s != -1]
            if not starts:
                break
            start = min(starts)
            try:
                obj, consumed = decoder.raw_decode(text[start:])
                last = obj
                idx = start + consumed
            except ValueError:
                idx = start + 1
        return last

    def get(self, endpoint, params=None):
        return self.request('GET', endpoint, params=params)

    def post(self, endpoint, data=None, params=None):
        return self.request('POST', endpoint, params=params, data=data)

    def put(self, endpoint, data=None, params=None):
        # Nagios XI reads PUT parameters from the query string (PHP does not
        # populate form data for PUT requests), so merge data into params.
        merged = dict(params or {})
        merged.update(data or {})
        return self.request('PUT', endpoint, params=merged)

    def delete(self, endpoint, params=None):
        return self.request('DELETE', endpoint, params=params)

    # ------------------------------------------------------------------ #
    # convenience
    # ------------------------------------------------------------------ #
    def fail(self, exc, **kwargs):
        self.module.fail_json(msg=to_native(exc), **kwargs)
