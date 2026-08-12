# -*- coding: utf-8 -*-

# Copyright (c) 2026, Chris Story <chris.story@effility.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r'''
options:
  url:
    description:
      - Base URL of the Nagios XI server, with or without the trailing
        C(/nagiosxi) path (e.g. C(https://nagios.example.com) or
        C(https://nagios.example.com/nagiosxi)).
    type: str
    required: true
  api_key:
    description:
      - API key of a Nagios XI user. Found under
        Admin -> Users -> Manage Users in the XI web interface.
    type: str
    required: true
  validate_certs:
    description:
      - Whether to validate TLS certificates when connecting over HTTPS.
    type: bool
    default: true
  timeout:
    description:
      - HTTP request timeout in seconds.
    type: int
    default: 30
requirements:
  - Nagios XI 5.x or later with the REST API enabled
notes:
  - All modules in this collection talk to the Nagios XI REST API
    (C(/nagiosxi/api/v1/)). Nagios Core alone does not expose this API.
  - Module defaults group C(group/community.nagios_cs.nagios_cs) can be used to
    set I(url), I(api_key), and I(validate_certs) once for all modules.
'''
