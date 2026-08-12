# Nagios XI API — Test Coverage Report

Suite: `run_all.yml` · Inventory: 100 simulated devices (`sim-web-001…sim-app-100`, IPs `127.0.1.1–127.0.1.100`)

The 127.0.1.x range answers ping locally on the Nagios server, so simulated
hosts genuinely go UP and produce real check results — which is what makes
status-based verification possible without real devices.

**Legend** — Covered: full round-trip verification (do it, then independently read it back).
Partial: API call verified to succeed, but the API offers no way to fully verify the outcome.
Conditional: covered only when runtime data exists. Missing: capability absent from the Nagios XI API itself.

---

## 1. objects/ section (read-only)

| API function | Test ID | Verification method | Status |
|---|---|---|---|
| GET objects/hoststatus | OBJ-01, SYS-CHK-01, SYS-CMD-01 | recordcount ≥ 100 for `lk:sim-` filter; `last_check` used to verify checks | Covered |
| GET objects/servicestatus | OBJ-01 | recordcount ≥ 10 for created PING services | Covered |
| GET objects/host | VER-HOST-01, VER-DEL-01 | 100 after create, 0 after delete | Covered |
| GET objects/service | VER-SVC-01, OBJ-01 | counts match created services | Covered |
| GET objects/hostgroup | VER-NAMED-01, OBJ-01 | created group found by name | Covered |
| GET objects/hostgroupmembers | OBJ-03 | structural (valid mapping returned) | Partial¹ |
| GET objects/servicegroup | VER-NAMED-01, OBJ-01 | created group found by name | Covered |
| GET objects/servicegroupmembers | OBJ-03 | structural | Partial¹ |
| GET objects/contact | VER-NAMED-01, OBJ-01 | created contact found | Covered |
| GET objects/contactgroup | VER-NAMED-01, OBJ-01 | created group found | Covered |
| GET objects/contactgroupmembers | OBJ-03 | structural | Partial¹ |
| GET objects/timeperiod | OBJ-02 | created timeperiod found | Covered |
| GET objects/command | OBJ-02 | created command found | Covered |
| GET objects/comment | OBJ-04 | comment added via corecommand appears, then disappears after DEL | Covered |
| GET objects/downtime | SYS-DT-01, OBJ-05 | scheduled downtime appears with internal ID, gone after delete | Covered |
| GET objects/logentries | OBJ-05 | structural (content is runtime history) | Partial |
| GET objects/statehistory | OBJ-05 | structural | Partial² |
| GET objects/notifications | OBJ-05 | structural | Partial² |
| GET objects/acknowledgements | OBJ-05 | structural | Partial² |
| GET objects/rrdexport | OBJ-06 | queried; RRDs only exist after checks have run a while | Conditional |
| GET objects/cpexport | OBJ-06 | queried; same dependency on perf data | Conditional |

¹ Member-list contents vary by XI version; the test asserts a valid response rather than exact membership.
² Fully verifying these requires generated history (real DOWN/CRITICAL events and notifications) — see §4.

## 2. config/ section (Core Config Manager)

Each type is tested through the full lifecycle. "Engine verify" = read back
through `objects/` after `applyconfig`; "CCM verify" = check-mode re-create
(changed=false ⇒ exists, changed=true ⇒ absent), which works even for types
the objects/ section doesn't expose.

| Object type | Create (POST) | Read (GET) | Update (PUT) | Delete (DELETE) |
|---|---|---|---|---|
| host (×100) | CFG-HOST-01 → VER-HOST-01 ✔ | VER-CCM-01 ✔ | CFG-HOST-02 (alias read back via objects/host) ✔ | DEL-HOST-01 → VER-DEL-01 ✔ |
| service (×10) | CFG-SVC-01 → VER-SVC-01 ✔ | VER-CCM-01 ✔ | CFG-UPD-01 (idempotent re-run) ✔ | DEL-SVC-01 → VER-DEL-01 ✔ |
| hostgroup | CFG-HG-01 → VER-NAMED-01 ✔ | VER-CCM-01 ✔ | CFG-UPD-01 ✔ | DEL-HOST-01 → VER-DEL-01 ✔ |
| servicegroup | CFG-SG-01 → VER-NAMED-01 ✔ | VER-CCM-01 ✔ | — (same PUT path; exercised implicitly) | DEL-SVC-01 → VER-DEL-01 ✔ |
| contact | CFG-CT-01 → VER-NAMED-01 ✔ | VER-CCM-01 ✔ | CFG-UPD-01 ✔ | DEL-MISC-01 → VER-DEL-01 ✔ |
| contactgroup | CFG-CG-01 → VER-NAMED-01 ✔ | VER-CCM-01 ✔ | — | DEL-MISC-01 → VER-DEL-01 ✔ |
| timeperiod | CFG-TP-01 → VER-NAMED-01 ✔ | VER-CCM-01 ✔ | CFG-UPD-01 ✔ | DEL-MISC-01 → VER-DEL-01 ✔ |
| command | CFG-CMD-01 → VER-NAMED-01 ✔ | VER-CCM-01 ✔ | CFG-UPD-01 ✔ | DEL-MISC-01 → VER-DEL-01 ✔ |
| hostescalation | CFG-HE-01 ✔ | VER-CCM-01 ✔ (CCM only³) | **Missing from API** (CFG-UPD-02) | DEL-DEP-01 ✔ (check-mode verify) |
| serviceescalation | CFG-SE-01 ✔ | VER-CCM-01 ✔ (CCM only³) | **Missing from API** (CFG-UPD-02) | DEL-DEP-01 ✔ |
| hostdependency | CFG-HD-01 ✔ | VER-CCM-01 ✔ (CCM only³) | **Missing from API** (CFG-UPD-02) | DEL-DEP-01 ✔ (check-mode verify) |
| servicedependency | CFG-SD-01 ✔ | VER-CCM-01 ✔ (CCM only³) | **Missing from API** (CFG-UPD-02) | DEL-DEP-01 ✔ |
| applyconfig | SYS-APPLY-01 / SYS-APPLY-02 — verified indirectly: engine-side objects/ queries only succeed after a working apply ✔ | | | |

³ The objects/ section has **no resources for escalations or dependencies**, so engine-side verification is impossible; only the CCM database can be checked.

## 3. system/ section

| API function | Test ID | Verification method | Status |
|---|---|---|---|
| GET system/info | SYS-INFO-01 | non-empty product/version payload | Covered |
| GET system/status | SYS-STAT-01 | valid payload | Covered |
| GET system/statusdetail | SYS-STAT-01 | valid payload | Covered |
| POST system/applyconfig | SYS-APPLY-01/02 | downstream objects/ queries reflect applied config | Covered |
| POST system/user (add) | SYS-USER-01 | user appears in `GET system/user`; second add reports no change | Covered |
| GET system/user (list) | SYS-USER-01/02 | used as the verifier for add/delete | Covered |
| DELETE system/user | SYS-USER-02 | user absent from subsequent list | Covered |
| POST system/authtoken | SYS-TOKEN-01 | token returned | Partial — see §4 |
| POST system/corecommand | OBJ-04, SYS-CMD-01 | side effects verified: comment appears/disappears; `last_check` advances after forced check | Covered⁴ |
| POST system/scheduleddowntime | SYS-DT-01 | entry appears in objects/downtime with internal ID | Covered |
| DELETE system/scheduleddowntime/&lt;id&gt; | SYS-DT-01 | entry gone from objects/downtime | Covered |
| POST system/massacknowledge | SYS-ACK-01 | API success only | Partial — see §4 |
| POST system/massimmediatecheck | SYS-CHK-01 | `last_check` timestamp advances on target host | Covered |

⁴ Two of the hundreds of possible external commands are round-trip verified; corecommand is a raw pass-through, so per-command coverage is inherently sample-based.

## 4. Items missing from the Nagios XI API

These are gaps in the API itself, not in the collection or the tests. Each is
recorded as SKIP/PARTIAL in the run report rather than silently ignored.

1. **No update (PUT) for escalations and dependencies.** These objects have no
   unique name/ID in the API, so they cannot be addressed for modification.
   Only create and delete work; changing one means delete + re-create. (CFG-UPD-02)
2. **No objects/ resources for escalations or dependencies.** Engine-side
   verification that they were applied is impossible; only the CCM record can
   be confirmed. (VER-CCM-01 note)
3. **No way to validate or list auth tokens.** `POST system/authtoken` returns
   a token, but there is no GET to confirm it works or is still valid — that
   would require an actual web login. (SYS-TOKEN-01)
4. **corecommand returns no execution result.** Submissions are fire-and-forget
   into the engine command pipe; success can only be inferred from side
   effects. Invalid commands can be silently discarded. (SYS-CMD-01)
5. **mass* endpoints return no per-object results.** massacknowledge and
   massimmediatecheck report overall submission only; verifying each target
   requires follow-up objects/ queries. (SYS-ACK-01, SYS-CHK-01)
6. **No API endpoint to modify an existing XI user.** system/user supports add,
   list, and delete only — no password reset or attribute change. (SYS-USER-01)
7. **Downtime can only be deleted by internal ID.** There is no
   delete-by-host/comment; the ID must first be discovered via
   objects/downtime. (SYS-DT-01 works around this.)
8. **No program-status endpoint.** Global engine flags (e.g. notifications
   enabled after `DISABLE_NOTIFICATIONS`) are not exposed anywhere in the API,
   so such corecommands cannot be verified at all.
9. **Acknowledgement verification requires a real problem state.** Because the
   127.0.1.x simulated hosts are all UP, there is nothing to acknowledge; the
   API also provides no way to inject a fake problem state other than passive
   check results via corecommand (`PROCESS_HOST_CHECK_RESULT` — usable as a
   manual extension of SYS-ACK-01 for hosts configured with passive checks).
10. **No CCM endpoints for hostextinfo/serviceextinfo or template management.**
    Object templates ("use" directives can be set as properties, but templates
    themselves cannot be created via the API).
11. **rrdexport/cpexport depend on perf data existing** — no API mechanism to
    force RRD creation, so first-run coverage is conditional. (OBJ-06)
12. Out of scope for the core API (separate components, not covered): BPI,
    Metrics/graphing component endpoints, notification settings per user.

## 5. Running the suite

```bash
cd tests
ansible-playbook -i inventory/hosts.yml run_all.yml \
  -e nagios_url=https://your-xi-server \
  -e nagios_api_key=YOUR_KEY
```

Every test records PASS / PARTIAL / SKIP / FAIL into
`tests/nagios_cs_test_report.md`; the run exits non-zero if anything FAILed.
Failures don't abort the suite — block/rescue records them and the remaining
tests still run, so one broken endpoint doesn't hide the rest of the results.
The suite is self-cleaning: playbook 04 deletes all `sim-*` objects and
verifies the deletions as its own set of tests.

## 6. Version differences observed (Nagios XI 2024-era releases)

A live run against an XI 2024 server confirmed these endpoints are absent
("Unknown API endpoint") on that release, in addition to the gaps in §4:
`config/{host,service}{escalation,dependency}` (all verbs), `objects/command`,
`objects/notifications`, `objects/acknowledgements`, `system/authtoken`, and
`system/massacknowledge`. The suite auto-detects these and records them as
SKIP ("missing from the API") rather than FAIL. The same run also confirmed
three behaviors now handled by the collection: PUT parameters must be passed
in the query string, users are deleted by numeric ID, and CCM identity fields
may be returned as lists.

## 7. API anomaly policy and known anomalies to report to Nagios

Policy (v1.1.0+): defects in the Nagios XI API are **surfaced, never coded
around**. The collection fails such requests with a diagnostic prefixed
`NAGIOS XI API ANOMALY`, and the test suite records them with status **BUG**
in a dedicated "report these to Nagios" section of the run report. SKIP is
reserved for endpoints that are absent from the tested release.

Anomalies confirmed against a live XI 2024-era server so far:

1. **config/timeperiod PUT leaks PHP debug output.** The endpoint prints a
   PHP `print_r()` dump of the submitted values before its JSON payload
   (`Array ( [type] => 9 ... ) {"success": "Updated ..."}`), producing an
   invalid mixed response body. The update itself is applied. Suggested
   report: "config/timeperiod PUT response contains print_r debug output
   before the JSON body." (Surfaced by CFG-UPD-01d.)
2. **objects/cpexport returns HTTP 500 when the requested track has no perf
   data** instead of a structured error or empty result set. Suggested
   report: "objects/cpexport should return a JSON error/empty payload, not
   an unhandled 500, when no perf data exists." (Surfaced by OBJ-06.)

Conforming behaviors that are *not* treated as anomalies (they match how the
API is documented/designed, so the collection implements them): PUT
parameters passed via the query string, user deletion by numeric ID, and CCM
identity fields returned as lists for multi-host objects.
