# Nagios XI collection - standalone test suite

Verification-driven tests for the `community.nagios_cs` collection, packaged
separately so the collection itself stays a clean, installable artifact.

## Contents

| Path | Purpose |
|---|---|
| `inventory/hosts.yml` | 100 simulated devices, IPs 127.0.1.1-127.0.1.100 |
| `01_config_tests.yml` | CCM create/verify/update/verify for all 12 object types |
| `02_objects_tests.yml` | all 21 read-only objects/ resources |
| `03_system_tests.yml` | every system/ endpoint with round-trip verification |
| `04_cleanup_delete_tests.yml` | delete tests + absence verification (self-cleaning) |
| `05_report.yml` | writes `nagios_cs_test_report.md` (PASS/PARTIAL/SKIP/FAIL) |
| `run_all.yml` | master runner (imports 01-05 in order) |
|  `../../docs/TEST_COVERAGE_REPORT.md` | static coverage map incl. gaps in the XI API itself |

## Prerequisites

1. ansible-core >= 2.14 on the control node.
2. The collection installed:

   ```bash
   ansible-galaxy collection install ../../community-nagios_cs-1.1.0.tar.gz (build from repo root with: ansible-galaxy collection build)
   # or, with the artifact next to this file:
   ansible-galaxy collection install -r requirements.yml
   ```

3. A **non-production** Nagios XI 5.x server and an API key with admin
   rights. The suite creates and deletes ~115 objects (all prefixed `sim-`)
   and applies the configuration several times, restarting the monitoring
   engine each time.

## Running

```bash
ansible-playbook -i inventory/hosts.yml run_all.yml \
  -e nagios_url=https://your-xi-server \
  -e nagios_api_key=YOUR_KEY
```

Or export `NAGIOS_URL` / `NAGIOS_API_KEY` and omit the `-e` flags
(see `vars.yml`).

Individual phases can be run alone, but 02/03 assume the objects created by
01 exist, and 04 expects to find them to delete. `run_all.yml` is the
supported entry point; it leaves the server clean and exits non-zero if any
test failed. Results land in `nagios_cs_test_report.md` next to the
playbooks.

## Why 127.0.1.x?

The whole 127.0.0.0/8 block answers ping locally on the Nagios server, so
the simulated devices genuinely go UP and generate real check results -
which is what lets the suite verify actions through live status data
(e.g. `last_check` advancing after a forced check) without any real devices.
