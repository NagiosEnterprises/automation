# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Unit tests for install-state detection, idempotency and failure reporting.

No package manager is touched: a fake module simulates rpm/dnf and
dpkg-query/apt-get against an in-memory "installed version".

Run with: ansible-test units --docker   (or plain pytest, see README notes)
"""
import pytest

from ansible_collections.nagios.ncpa.plugins.module_utils import (
    ncpa_common, rhel, debian
)

OS_EL9 = {"ID": "rhel", "VERSION_ID": "9.4"}
OS_DEB12 = {"ID": "debian", "VERSION_ID": "12", "VERSION_CODENAME": "bookworm"}


class FakeModule:
    def __init__(self, params, check_mode=False, installed=None,
                 fail_install=False, install_noop=False, fail_remove=False):
        self.params = dict({"state": "present", "package_source": "package",
                            "version": None, "install_method": "package"}, **params)
        self.check_mode = check_mode
        self.installed = installed          # e.g. "3.1.1" or None
        self.fail_install = fail_install    # package manager returns rc 1
        self.install_noop = install_noop    # rc 0 but nothing installed
        self.fail_remove = fail_remove
        self.calls = []

    def get_bin_path(self, name):
        return "/usr/bin/" + name

    def run_command(self, cmd):
        self.calls.append(cmd)
        tool, args = cmd[0].rsplit("/", 1)[-1], cmd[1:]

        if tool == "rpm" and "-q" in args:
            return (0, self.installed, "") if self.installed else (1, "package ncpa is not installed", "")
        if tool == "dpkg-query":
            if self.installed:
                return 0, "install ok installed\t" + self.installed + "-1", ""
            return 1, "", "dpkg-query: no packages found matching ncpa"
        if tool in ("dnf", "apt-get") and "install" in args and any("ncpa" in a for a in args):
            if self.fail_install:
                return 1, "", "simulated install failure"
            if not self.install_noop:
                self.installed = self.params["version"] or "3.1.1"
            return 0, "", ""
        if tool in ("dnf", "apt-get") and "remove" in args:
            if self.fail_remove:
                return 1, "", "simulated remove failure"
            self.installed = None
            return 0, "", ""
        return 0, "", ""   # rpm --import, systemctl, apt-get update, gpg, prereqs

    def ran(self, verb):
        return [c for c in self.calls if verb in c and ("dnf" in c[0] or "apt-get" in c[0])]


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    for mod in (rhel, debian):
        monkeypatch.setattr(mod, "parse_os_release", lambda: OS_EL9 if mod is rhel else OS_DEB12)
        monkeypatch.setattr(mod, "detect_architecture", lambda m: "x86_64")
    monkeypatch.setattr(debian, "download_file", lambda url, dest: None)


HANDLERS = [pytest.param(rhel.handle_rhel, id="rhel"),
            pytest.param(debian.handle_deb, id="debian")]


# ------------------------------------------------------------ helpers
@pytest.mark.parametrize("installed, requested, expected", [
    (None, None, False),
    ("3.1.1", None, True),
    ("3.1.1", "latest", True),
    ("3.1.1", "3.1.1", True),
    ("3.1.1-1", "3.1.1", True),
    ("3.1.1", "3.2.0", False),
])
def test_version_satisfied(installed, requested, expected):
    assert ncpa_common.version_satisfied(installed, requested) is expected


def test_dpkg_config_files_state_is_not_installed():
    m = FakeModule({})
    m.run_command = lambda cmd: (0, "deinstall ok config-files\t3.1.1-1", "")
    assert ncpa_common.get_installed_ncpa_version(m, {"dpkg_query": "/usr/bin/dpkg-query"}) is None


# ------------------------------------------------------------ present
@pytest.mark.parametrize("handler", HANDLERS)
def test_install_when_absent_changes(handler):
    m = FakeModule({})
    r = handler(m)
    assert r["changed"] is True and not r.get("failed")
    assert r["installed_version"].split("-")[0] == "3.1.1"


@pytest.mark.parametrize("handler", HANDLERS)
def test_install_when_present_is_idempotent(handler):
    m = FakeModule({}, installed="3.1.1")
    r = handler(m)
    assert r["changed"] is False and not r.get("failed")
    assert m.ran("install") == []


@pytest.mark.parametrize("handler", HANDLERS)
def test_install_different_version_changes(handler):
    m = FakeModule({"version": "3.2.0"}, installed="3.1.1")
    r = handler(m)
    assert r["changed"] is True and r["installed_version"].split("-")[0] == "3.2.0"


@pytest.mark.parametrize("handler", HANDLERS)
def test_install_failure_is_reported_as_failed(handler):
    r = handler(FakeModule({}, fail_install=True))
    assert r["failed"] is True and r["changed"] is False


@pytest.mark.parametrize("handler", HANDLERS)
def test_install_rc0_but_not_installed_is_failed(handler):
    r = handler(FakeModule({}, install_noop=True))
    assert r["failed"] is True


@pytest.mark.parametrize("handler", HANDLERS)
@pytest.mark.parametrize("installed, expected", [(None, True), ("3.1.1", False)])
def test_check_mode_present(handler, installed, expected):
    m = FakeModule({}, check_mode=True, installed=installed)
    assert handler(m)["changed"] is expected
    assert m.ran("install") == []


# ------------------------------------------------------------ absent
@pytest.mark.parametrize("handler", HANDLERS)
def test_remove_when_present_changes(handler):
    m = FakeModule({"state": "absent"}, installed="3.1.1")
    r = handler(m)
    assert r["changed"] is True and m.installed is None


@pytest.mark.parametrize("handler", HANDLERS)
def test_remove_when_absent_is_idempotent(handler):
    m = FakeModule({"state": "absent"})
    r = handler(m)
    assert r["changed"] is False and m.ran("remove") == []


@pytest.mark.parametrize("handler", HANDLERS)
def test_remove_failure_is_reported_as_failed(handler):
    r = handler(FakeModule({"state": "absent"}, installed="3.1.1", fail_remove=True))
    assert r["failed"] is True and r["changed"] is False


@pytest.mark.parametrize("handler", HANDLERS)
@pytest.mark.parametrize("installed, expected", [(None, False), ("3.1.1", True)])
def test_check_mode_absent(handler, installed, expected):
    m = FakeModule({"state": "absent"}, check_mode=True, installed=installed)
    assert handler(m)["changed"] is expected
    assert m.ran("remove") == []
