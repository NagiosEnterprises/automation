# Nagios XI REST API — Ansible Collection Reference

**Collection:** `community.nagios_cs` v1.1.0 · **Community** · July 2026

API function reference with copy-and-paste playbook samples for every module.

---

## Table of Contents

- [1. Getting started](#1-getting-started)
- [2. Objects section (read-only queries)](#2-objects-section-read-only-queries)
  - [object_info](#object_info)
- [3. Config section (Core Config Manager)](#3-config-section-core-config-manager)
  - [host](#host) · [service](#service) · [hostgroup](#hostgroup) · [servicegroup](#servicegroup) · [contact](#contact) · [contactgroup](#contactgroup) · [timeperiod](#timeperiod) · [command](#command) · [hostescalation](#hostescalation) · [serviceescalation](#serviceescalation) · [hostdependency](#hostdependency) · [servicedependency](#servicedependency)
- [4. System section (operations)](#4-system-section-operations)
  - [apply_config](#apply_config) · [system_info](#system_info) · [system_status](#system_status) · [user](#user) · [user_info](#user_info) · [auth_token](#auth_token) · [core_command](#core_command) · [scheduled_downtime](#scheduled_downtime) · [mass_acknowledge](#mass_acknowledge) · [mass_immediate_check](#mass_immediate_check)
- [Appendix A. Known API gaps and anomalies (XI 2024-era releases)](#appendix-a-known-api-gaps-and-anomalies-xi-2024-era-releases)

---

## 1. Getting started

All modules in the `community.nagios_cs` collection talk to the Nagios XI REST API (`/nagiosxi/api/v1/`). The API is organized into three sections: **objects** (read-only status and history), **config** (Core Config Manager CRUD), and **system** (operational actions). Authentication uses an API key from an XI user (Admin → Users → Manage Users).

### Installation

```bash
ansible-galaxy collection install community-nagios_cs-1.1.0.tar.gz
# or from the GitHub repository:
ansible-galaxy collection install git+https://github.com/ansible-collections/community.nagios_cs.git
```

### Connection options (every module)

| Option | Description |
|---|---|
| `url` | Base URL of the XI server, with or without the trailing `/nagiosxi` path. Required. |
| `api_key` | API key of an XI user. Required. Store in Ansible Vault. |
| `validate_certs` | Validate TLS certificates; default `true`. |
| `timeout` | HTTP timeout in seconds; default `30`. |

### Recommended playbook skeleton

Set the connection once for every module using the collection's `module_defaults` action group, then paste any task from this document into the `tasks:` list:

```yaml
---
- name: Manage Nagios XI
  hosts: localhost
  gather_facts: false
  vars:
    nagios_url: https://nagios.example.com
    nagios_api_key: "{{ vault_nagios_api_key }}"
  module_defaults:
    group/community.nagios_cs.nagios_cs:
      url: "{{ nagios_url }}"
      api_key: "{{ nagios_api_key }}"
      validate_certs: false
  tasks:
    # paste any task from this document here
```

> **API anomaly policy:** defects in the Nagios XI API (malformed responses, unhandled HTTP 500s) are surfaced by the collection as errors prefixed `NAGIOS XI API ANOMALY`, containing the evidence needed for a bug report to Nagios. They are never silently worked around. See [Appendix A](#appendix-a-known-api-gaps-and-anomalies-xi-2024-era-releases).

---

## 2. Objects section (read-only queries)

The objects section is read-only and returns status, configuration, and historical data as JSON. One module covers every resource.

### object_info

**Module:** `community.nagios_cs.object_info` · **API endpoint:** `objects/<resource>` · **HTTP verbs:** GET

Queries any objects resource. The `resource` option selects the endpoint; the free-form `query` dict is passed straight through as URL parameters for filtering, paging (`records: "100:0"`), ordering (`orderby: "host_name:a"`), and time ranges (`starttime`/`endtime` as epoch seconds). Filter operators include exact match (`host_name: web01`), LIKE (`host_name: "lk:web"`), and IN (`host_name: "in:web01,web02"`).

| Option | Description |
|---|---|
| `resource` | One of the 21 resources listed below. Required. |
| `query` | Dict of filter/paging/ordering parameters passed through to the API. |

```yaml
- name: All hosts currently DOWN
  community.nagios_cs.object_info:
    resource: hoststatus
    query:
      current_state: 1
  register: down_hosts

- name: First 100 service statuses for web01
  community.nagios_cs.object_info:
    resource: servicestatus
    query:
      host_name: web01
      records: "100:0"

- name: State history for the last 24 hours
  community.nagios_cs.object_info:
    resource: statehistory
    query:
      starttime: "{{ ('%s' | strftime | int) - 86400 }}"
      endtime: "{{ '%s' | strftime | int }}"

- name: Find a downtime ID for deletion
  community.nagios_cs.object_info:
    resource: downtime
    query:
      host_name: web01
  register: dt
```

#### Available resources

| Resource | Returns |
|---|---|
| `hoststatus` | Current state of hosts (up/down, last check, output). Filters: `host_name`, `current_state`, `records`, `orderby`. |
| `servicestatus` | Current state of services. Filters: `host_name`, `name`/`service_description`, `current_state`. |
| `host` | Host object definitions as loaded by the engine. |
| `service` | Service object definitions as loaded by the engine. |
| `hostgroup` | Host group definitions. |
| `hostgroupmembers` | Host groups with their member hosts. |
| `servicegroup` | Service group definitions. |
| `servicegroupmembers` | Service groups with their member services. |
| `contact` | Contact definitions. |
| `contactgroup` | Contact group definitions. |
| `contactgroupmembers` | Contact groups with their member contacts. |
| `timeperiod` | Time period definitions. |
| `command` | Command definitions. *Absent on some XI releases (verified missing on XI 2024).* |
| `comment` | Host/service comments currently in the engine. |
| `downtime` | Scheduled downtime entries, including `internal_downtime_id` needed for deletion. |
| `logentries` | Engine log entries. Supports `starttime`/`endtime` epoch filters. |
| `statehistory` | Historical state changes. |
| `notifications` | Notification history. *Absent on some XI releases.* |
| `acknowledgements` | Acknowledgement history. *Absent on some XI releases.* |
| `rrdexport` | Performance data export from RRDs (requires perf data to exist). |
| `cpexport` | Perf-data export; requires `host_name`, `service_description`, and `track`. *Returns HTTP 500 when no data exists (reported to Nagios as an API defect).* |

---

## 3. Config section (Core Config Manager)

The config section creates, updates, and deletes monitoring objects. Every module below is idempotent, supports check mode, and takes `state` (present/absent), `applyconfig`, and a free-form `properties` dict of standard Nagios directives. Objects are inactive in the engine until the configuration is applied — for bulk changes, apply once at the end with [apply_config](#apply_config).

Common options for all twelve modules (in addition to the identity options listed per module):

| Option | Description |
|---|---|
| `state` | `present` (default) or `absent`. |
| `applyconfig` | `true` to apply the configuration inline (restarts the monitoring engine); default `false`. |
| `properties` | Dict of standard Nagios directives passed through to the CCM (`alias`, `address`, `check_command`, `max_check_attempts`, `contacts`, `members`, …). Use quoted strings for numbers, e.g. `"5"`, for clean idempotency. |

### host

**Module:** `community.nagios_cs.host` · **API endpoint:** `config/host` (DELETE/PUT: `config/host/<host_name>`) · **HTTP verbs:** GET, POST, PUT, DELETE

Creates, updates, and deletes host definitions. Identity: `host_name` (required).

```yaml
- name: Ensure a monitored host exists
  community.nagios_cs.host:
    host_name: web01
    properties:
      alias: Web server 01
      address: 192.168.1.50
      check_command: check-host-alive!3000,80%!5000,100%
      max_check_attempts: "5"
      check_period: 24x7
      contacts: nagiosadmin
      notification_interval: "5"
      notification_period: 24x7

- name: Remove a host (and apply immediately)
  community.nagios_cs.host:
    host_name: web01
    state: absent
    applyconfig: true
```

### service

**Module:** `community.nagios_cs.service` · **API endpoint:** `config/service` (DELETE/PUT: `config/service/<host_name>/<service_description>`) · **HTTP verbs:** GET, POST, PUT, DELETE

Creates, updates, and deletes service definitions. Identity: `host_name` + `service_description` (both required).

```yaml
- name: Ensure an HTTP service exists on web01
  community.nagios_cs.service:
    host_name: web01
    service_description: HTTP
    properties:
      check_command: check_http
      max_check_attempts: "5"
      check_interval: "5"
      retry_interval: "1"
      check_period: 24x7
      notification_interval: "5"
      notification_period: 24x7
      contacts: nagiosadmin
```

### hostgroup

**Module:** `community.nagios_cs.hostgroup` · **API endpoint:** `config/hostgroup` · **HTTP verbs:** GET, POST, PUT, DELETE

Creates, updates, and deletes host groups. Identity: `hostgroup_name` (required).

```yaml
- name: Ensure a host group exists
  community.nagios_cs.hostgroup:
    hostgroup_name: web-servers
    properties:
      alias: Web Servers
      members: web01,web02
```

### servicegroup

**Module:** `community.nagios_cs.servicegroup` · **API endpoint:** `config/servicegroup` · **HTTP verbs:** GET, POST, PUT, DELETE

Creates, updates, and deletes service groups. Identity: `servicegroup_name` (required).

```yaml
- name: Ensure a service group exists
  community.nagios_cs.servicegroup:
    servicegroup_name: http-checks
    properties:
      alias: HTTP Checks
      members: web01,HTTP,web02,HTTP
```

> **Note:** `members` is a flat comma list of `host,service` pairs.

### contact

**Module:** `community.nagios_cs.contact` · **API endpoint:** `config/contact` · **HTTP verbs:** GET, POST, PUT, DELETE

Creates, updates, and deletes contacts. Identity: `contact_name` (required).

```yaml
- name: Ensure a contact exists
  community.nagios_cs.contact:
    contact_name: jane-ops
    properties:
      alias: Jane Ops
      email: jane@example.com
      host_notifications_enabled: "1"
      service_notifications_enabled: "1"
      host_notification_period: 24x7
      service_notification_period: 24x7
      host_notification_options: d,u,r
      service_notification_options: w,u,c,r
      host_notification_commands: notify-host-by-email
      service_notification_commands: notify-service-by-email
```

> **Note:** `host_notifications_enabled` and `service_notifications_enabled` are required by the CCM on XI 2024-era releases.

### contactgroup

**Module:** `community.nagios_cs.contactgroup` · **API endpoint:** `config/contactgroup` · **HTTP verbs:** GET, POST, PUT, DELETE

Creates, updates, and deletes contact groups. Identity: `contactgroup_name` (required).

```yaml
- name: Ensure a contact group exists
  community.nagios_cs.contactgroup:
    contactgroup_name: on-call
    properties:
      alias: On-call rotation
      members: jane-ops
```

### timeperiod

**Module:** `community.nagios_cs.timeperiod` · **API endpoint:** `config/timeperiod` · **HTTP verbs:** GET, POST, PUT, DELETE

Creates, updates, and deletes time periods. Identity: `timeperiod_name` (required).

```yaml
- name: Ensure a business-hours time period exists
  community.nagios_cs.timeperiod:
    timeperiod_name: business-hours
    properties:
      alias: Business Hours
      monday: "09:00-17:00"
      tuesday: "09:00-17:00"
      wednesday: "09:00-17:00"
      thursday: "09:00-17:00"
      friday: "09:00-17:00"
```

> **Known API anomaly:** on XI 2024-era releases the timeperiod PUT (update) response contains leaked PHP debug output; the module fails with a `NAGIOS XI API ANOMALY` diagnostic to report to Nagios. Creation and deletion are unaffected.

### command

**Module:** `community.nagios_cs.command` · **API endpoint:** `config/command` · **HTTP verbs:** GET, POST, PUT, DELETE

Creates, updates, and deletes command definitions. Identity: `command_name` (required).

```yaml
- name: Ensure a check command exists
  community.nagios_cs.command:
    command_name: check_custom_ping
    properties:
      command_line: "$USER1$/check_ping -H $HOSTADDRESS$ -w $ARG1$ -c $ARG2$ -p 5"
```

### hostescalation

**Module:** `community.nagios_cs.hostescalation` · **API endpoint:** `config/hostescalation` · **HTTP verbs:** GET, POST, DELETE (no PUT in the API)

Creates and deletes host escalations. Identity: `host_name` (required).

```yaml
- name: Escalate long-running host problems
  community.nagios_cs.hostescalation:
    host_name: web01
    properties:
      first_notification: "3"
      last_notification: "0"
      notification_interval: "30"
      contact_groups: on-call
```

> **Note:** escalation/dependency endpoints are absent on some XI releases (verified missing on XI 2024), and the API defines no PUT for them anywhere — updates require delete + re-create. Idempotency is best-effort because Nagios does not enforce uniqueness for these object types.

### serviceescalation

**Module:** `community.nagios_cs.serviceescalation` · **API endpoint:** `config/serviceescalation` · **HTTP verbs:** GET, POST, DELETE (no PUT in the API)

Creates and deletes service escalations. Identity: `host_name` + `service_description` (required).

```yaml
- name: Escalate long-running service problems
  community.nagios_cs.serviceescalation:
    host_name: web01
    service_description: HTTP
    properties:
      first_notification: "3"
      last_notification: "0"
      notification_interval: "15"
      contact_groups: on-call
```

> **Note:** same availability and update caveats as [hostescalation](#hostescalation).

### hostdependency

**Module:** `community.nagios_cs.hostdependency` · **API endpoint:** `config/hostdependency` · **HTTP verbs:** GET, POST, DELETE (no PUT in the API)

Creates and deletes host dependencies. Identity: `host_name` (master) + `dependent_host_name` (required).

```yaml
- name: web02 depends on web01
  community.nagios_cs.hostdependency:
    host_name: web01
    dependent_host_name: web02
    properties:
      notification_failure_criteria: d,u
      execution_failure_criteria: d,u
```

> **Note:** same availability and update caveats as [hostescalation](#hostescalation).

### servicedependency

**Module:** `community.nagios_cs.servicedependency` · **API endpoint:** `config/servicedependency` · **HTTP verbs:** GET, POST, DELETE (no PUT in the API)

Creates and deletes service dependencies. Identity: `host_name` + `service_description` (master) + `dependent_host_name` + `dependent_service_description` (required).

```yaml
- name: HTTP on web02 depends on HTTP on web01
  community.nagios_cs.servicedependency:
    host_name: web01
    service_description: HTTP
    dependent_host_name: web02
    dependent_service_description: HTTP
    properties:
      notification_failure_criteria: w,u,c
```

> **Note:** same availability and update caveats as [hostescalation](#hostescalation).

---

## 4. System section (operations)

The system section performs operational actions: applying configuration, reading system state, managing users and tokens, scheduling downtime, acknowledging problems, forcing checks, and submitting raw engine commands.

### apply_config

**Module:** `community.nagios_cs.apply_config` · **API endpoint:** `system/applyconfig` · **HTTP verbs:** POST

Writes pending Core Config Manager changes to the monitoring engine and restarts it. Run once after a batch of config changes rather than per-object. Always reports `changed=true` when submitted.

```yaml
- name: Apply pending configuration changes
  community.nagios_cs.apply_config:
```

> **Note:** every apply restarts the monitoring engine; allow the engine a short time to reload before verifying via objects queries.

### system_info

**Module:** `community.nagios_cs.system_info` · **API endpoint:** `system/info` · **HTTP verbs:** GET

Returns product and version information for the XI installation, including the version string. Useful for health checks and for including in bug reports to Nagios.

```yaml
- name: Determine the current Nagios XI version
  community.nagios_cs.system_info:
  register: xi

- name: Show the version
  ansible.builtin.debug:
    msg: "Nagios XI version: {{ xi.info.version }}"
```

### system_status

**Module:** `community.nagios_cs.system_status` · **API endpoint:** `system/status` (`system/statusdetail` with `detailed: true`) · **HTTP verbs:** GET

Returns the state of the XI daemons and monitoring engine.

| Option | Description |
|---|---|
| `detailed` | `true` to query `system/statusdetail`; default `false`. |

```yaml
- name: Check daemon status in detail
  community.nagios_cs.system_status:
    detailed: true
  register: status
```

### user

**Module:** `community.nagios_cs.user` · **API endpoint:** `system/user` (DELETE by numeric ID: `system/user/<user_id>`) · **HTTP verbs:** GET, POST, DELETE

Creates and deletes XI web interface users. Existing users are detected via the user list; deletion resolves the numeric user ID automatically (required on XI 2024-era releases) with a legacy username fallback. The API offers no way to modify an existing user.

| Option | Description |
|---|---|
| `username` | Login name. Required. |
| `state` | `present` (default) or `absent`. |
| `name` / `email` / `password` | Required when creating a user. |
| `auth_level` | `user` (default) or `admin`. |
| `force_pw_change` | Force a password change at first login; default `false`. |
| `extra` | Dict of additional parameters (`phone`, `language`, `auth_type`, …). |

```yaml
- name: Create an XI user
  community.nagios_cs.user:
    username: jdoe
    name: Jane Doe
    email: jdoe@example.com
    password: "{{ vault_jdoe_password }}"
    auth_level: user
    force_pw_change: true

- name: Remove an XI user
  community.nagios_cs.user:
    username: jdoe
    state: absent
```

### user_info

**Module:** `community.nagios_cs.user_info` · **API endpoint:** `system/user` · **HTTP verbs:** GET

Lists XI web interface users. Used to verify user creation/deletion and to look up user attributes.

```yaml
- name: List all XI users
  community.nagios_cs.user_info:
  register: users
```

### auth_token

**Module:** `community.nagios_cs.auth_token` · **API endpoint:** `system/authtoken` · **HTTP verbs:** POST

Creates a short-lived authentication token for a user, typically used to build auto-login URLs into the XI interface.

| Option | Description |
|---|---|
| `username` | User the token is for. Required. |
| `valid_min` | Token lifetime in minutes; default `5`. |

```yaml
- name: Mint a 15-minute auto-login token
  community.nagios_cs.auth_token:
    username: dashboard
    valid_min: 15
  register: token
```

> **Note:** endpoint is absent on some XI releases (verified missing on XI 2024). The API provides no way to validate or list tokens.

### core_command

**Module:** `community.nagios_cs.core_command` · **API endpoint:** `system/corecommand` · **HTTP verbs:** POST

Submits any raw Nagios Core external command to the engine (the same commands accepted by the engine command pipe). This covers every engine action that lacks a dedicated module: enabling/disabling notifications, forced checks, passive check results, comment management, and so on. Fire-and-forget: the API returns no per-command result, so verify by side effect (e.g. `hoststatus` `last_check`).

| Option | Description |
|---|---|
| `command` | The external command string without the leading bracketed timestamp. Required. |

```yaml
- name: Force an immediate host check
  community.nagios_cs.core_command:
    command: "SCHEDULE_FORCED_HOST_CHECK;web01;{{ '%s' | strftime }}"

- name: Add a host comment
  community.nagios_cs.core_command:
    command: "ADD_HOST_COMMENT;web01;1;ansible;Patched by automation"
```

### scheduled_downtime

**Module:** `community.nagios_cs.scheduled_downtime` · **API endpoint:** `system/scheduleddowntime` (DELETE: `system/scheduleddowntime/<id>`) · **HTTP verbs:** POST, DELETE

Schedules downtime for hosts, host groups, or service groups, and cancels an entry by its internal downtime ID. Find the ID by querying [object_info](#object_info) with `resource: downtime`.

| Option | Description |
|---|---|
| `state` | `present` (default, schedules) or `absent` (deletes by `downtime_id`). |
| `comment` / `start` / `end` | Required for `present`. `start`/`end` are epoch seconds. |
| `hosts` / `hostgroups` / `servicegroups` | Lists of targets. |
| `all_services` | Also cover all services on the given hosts; default `false`. |
| `downtime_id` | Internal ID; required for `absent`. |

```yaml
- name: 2-hour maintenance window for the web tier
  community.nagios_cs.scheduled_downtime:
    comment: Patching window OPS-1234
    start: "{{ '%s' | strftime | int }}"
    end: "{{ ('%s' | strftime | int) + 7200 }}"
    hosts: [web01, web02]
    all_services: true

- name: Cancel downtime entry 10
  community.nagios_cs.scheduled_downtime:
    state: absent
    downtime_id: 10
```

### mass_acknowledge

**Module:** `community.nagios_cs.mass_acknowledge` · **API endpoint:** `system/massacknowledge` · **HTTP verbs:** POST

Acknowledges current problems on hosts and/or services in one request. Services are written as `host_name!service_description`.

| Option | Description |
|---|---|
| `comment` | Comment recorded with the acknowledgement. |
| `hosts` / `services` | Targets; at least one list is required. |
| `sticky` / `notify` / `persistent` | Standard acknowledgement flags. |

```yaml
- name: Acknowledge problems on two hosts
  community.nagios_cs.mass_acknowledge:
    comment: Known issue, ticket OPS-1234
    hosts: [web01, web02]
    services:
      - "web01!HTTP"
```

> **Note:** endpoint is absent on some XI releases (verified missing on XI 2024); use [core_command](#core_command) with `ACKNOWLEDGE_HOST_PROBLEM` / `ACKNOWLEDGE_SVC_PROBLEM` as the engine-level alternative.

### mass_immediate_check

**Module:** `community.nagios_cs.mass_immediate_check` · **API endpoint:** `system/massimmediatecheck` · **HTTP verbs:** POST

Schedules an immediate check of the given hosts and/or services. Verify by watching `last_check` advance in `objects/hoststatus`.

| Option | Description |
|---|---|
| `hosts` / `services` | Targets; at least one list is required. Services are `host_name!service_description`. |

```yaml
- name: Recheck the web tier now
  community.nagios_cs.mass_immediate_check:
    hosts: [web01, web02]
    services:
      - "web01!HTTP"
```

---

## Appendix A. Known API gaps and anomalies (XI 2024-era releases)

Verified against a live Nagios XI 2024 server using the collection's test suite (`tests/live` in the repository). Two categories:

### Endpoints missing from the release (SKIP in test reports)

| Endpoint | Impact / alternative |
|---|---|
| `config/hostescalation`, `config/serviceescalation`, `config/hostdependency`, `config/servicedependency` | Escalations and dependencies cannot be managed via the API on affected releases; manage them in the Core Config Manager UI. |
| `objects/command` | Command definitions cannot be read from the objects section; existence can still be verified via the config section (check mode). |
| `objects/notifications`, `objects/acknowledgements` | Notification and acknowledgement history unavailable via the API. |
| `system/authtoken` | Auto-login tokens cannot be minted via the API. |
| `system/massacknowledge` | Use [core_command](#core_command) with `ACKNOWLEDGE_HOST_PROBLEM` / `ACKNOWLEDGE_SVC_PROBLEM` instead. |

### API defects to report to Nagios (BUG in test reports)

| Defect | Detail |
|---|---|
| `config/timeperiod` PUT leaks PHP debug output | The update response contains a `print_r()` dump before the JSON payload, producing an invalid body. The update is applied; the collection fails the call with a `NAGIOS XI API ANOMALY` diagnostic. |
| `objects/cpexport` returns HTTP 500 with no data | When the requested track has no performance data, the endpoint returns an unhandled 500 instead of a structured error or empty result. |

Include the XI version (from [system_info](#system_info)) and the full anomaly diagnostic text in any report to Nagios.
