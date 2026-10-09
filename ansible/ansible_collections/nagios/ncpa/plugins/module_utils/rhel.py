from ansible_collections.nagios.ncpa.plugins.module_utils.ncpa_common import (
    parse_os_release,
    detect_architecture,
    get_installed_ncpa_version,
    version_satisfied,
    is_nagios_repo_installed,
    get_os_major_version
)

def build_rpm_url(version, major_release, architecture):
    base_url = "https://assets.nagios.com/downloads/ncpa3"

    if version in [None, "", "latest"]:
        filename = f"ncpa-latest-1.{architecture}.rpm"
    else:
        filename = f"ncpa-{version}-1.el{major_release}.{architecture}.rpm"

    return f"{base_url}/{filename}"

def remove_ncpa(module,paths):
    return module.run_command(
        [paths["dnf"], "remove", "-y", "ncpa"]
    )

def remove_rhel_repo(module,paths):
    rc = module.run_command(
        [paths["dnf"], "remove -y", "nagios-repo"]
    )

    return rc == 0


def handle_rhel(module):
    changed = False
    pkg_mgr = module.get_bin_path("dnf") or module.get_bin_path("yum")
    paths = {
        "rpm": module.get_bin_path("rpm") or "rpm",
        "dnf": pkg_mgr
    }

    if not pkg_mgr:
        return {
            "failed": True,
            "changed": False,
            "msg": "ERROR: Neither dnf nor yum was found on this host."
        }

    version = module.params.get("version")
    package_source = module.params.get("package_source")
    installed_version = get_installed_ncpa_version(module, paths)
    satisfied = version_satisfied(installed_version, version)

    if module.params.get("state") == "present":

        if module.check_mode:
            would_change = not satisfied
            if package_source == "repository" and not is_nagios_repo_installed(module, paths):
                would_change = True
            return {
                "changed": would_change,
                "msg": (
                    "NCPA would be installed or changed."
                    if would_change else
                    "NCPA {0} is already installed, no changes would be made.".format(installed_version)
                ),
                "installed_version": installed_version
            }

        os_release = parse_os_release()
        major_release = get_os_major_version(os_release)
        architecture = detect_architecture(module)

        if package_source == "package":

            if satisfied:
                return {
                    "changed": False,
                    "msg": "NCPA {0} is already installed".format(installed_version),
                    "installed_version": installed_version
                }

            url = build_rpm_url(
                version,
                major_release,
                architecture
            )

            if not url:
                return {
                    "failed": True,
                    "changed": changed,
                    "msg": "ERROR: Failed to build URL"
                }

            cmd = [
                paths["dnf"],
                "-y",
                "install",
                url
            ]

            rc, stdout, stderr = module.run_command(cmd)

            if rc != 0:
                return {
                    "failed": True,
                    "changed": changed,
                    "msg": "ERROR: Failed to install NCPA",
                    "stderr": stderr
                }

            new_version = get_installed_ncpa_version(module, paths)

            if not version_satisfied(new_version, version):
                return {
                    "failed": True,
                    "changed": new_version != installed_version,
                    "msg": (
                        "ERROR: dnf reported success, but the installed NCPA "
                        "version is {0} (requested {1})"
                    ).format(new_version, version or "latest"),
                    "installed_version": new_version
                }

            return {
                "changed": new_version != installed_version,
                "msg": "NCPA installed successfully",
                "installed_version": new_version
            }

        elif package_source == "repository":

            repo_dash_map = {
                "8": 2,
                "9": 2,
                "10": 1
            }
            repo_dash_num = repo_dash_map.get(major_release)
            if repo_dash_num is None:
                return {
                    "failed": True,
                    "changed": False,
                    "msg": (
                        "ERROR: Unsupported Enterprise Linux version {0}. "
                        "Supported: 8, 9, 10."
                    ).format(major_release)
                }

            repo_url = (
                f"https://repo.nagios.com/nagios/"
                f"{major_release}/"
                f"nagios-repo-{major_release}"
                f"-{repo_dash_num}.el{major_release}.noarch.rpm"
            )

            if not is_nagios_repo_installed(module,paths):
                rc, stdout, stderr = module.run_command(
                    [paths["dnf"], "install", "-y", repo_url]
                )
                if rc != 0:
                    return {
                        "failed": True,
                        "changed": changed,
                        "msg": f"ERROR: Failed to install the nagios-repo rpm, URL {repo_url}",
                        "stderr": stderr
                    }
                changed = True

            if satisfied:
                return {
                    "changed": changed,
                    "msg": "NCPA {0} is already installed".format(installed_version),
                    "installed_version": installed_version
                }

            rc, stdout, stderr = module.run_command(
                [paths["rpm"], "--import", "https://repo.nagios.com/GPG-KEY-NAGIOS-V2"]
            )

            if rc != 0:
                return {
                    "failed": True,
                    "changed": changed,
                    "msg": "ERROR: Failed to add Nagios repo key V2",
                    "stderr": stderr
                }

            rc, stdout, stderr = module.run_command(
                [paths["rpm"], "--import", "https://repo.nagios.com/GPG-KEY-NAGIOS-V3"]
            )

            if rc != 0:
                return {
                    "failed": True,
                    "changed": changed,
                    "msg": "ERROR: Failed to add Nagios repo key v3",
                    "stderr": stderr
                }

            rc, stdout, stderr = module.run_command(
                [paths["dnf"], "install", "-y", "ncpa"]
            )

            if rc != 0:
                return {
                    "failed": True,
                    "changed": changed,
                    "msg": "ERROR: Failed to install NCPA",
                    "stderr": stderr
                }

            new_version = get_installed_ncpa_version(module, paths)
            if new_version is None:
                return {
                    "failed": True,
                    "changed": changed,
                    "msg": "ERROR: dnf reported success, but NCPA is not installed"
                }

            rc, stdout, stderr = module.run_command(
                ["systemctl", "enable", "ncpa"]
            )

            if rc != 0:
                return {
                    "failed": True,
                    "changed": True,
                    "msg": "ERROR: NCPA installed, but failed to set it to start on boot",
                    "stderr": stderr
                }

            return {
                "changed": True,
                "msg": "Nagios repository, and NCPA installed successfully.",
                "installed_version": new_version
            }

        else:
            return {
                "failed": True,
                "changed": False,
                "msg": f"ERROR: Unknown package_source {package_source}"
            }

    elif module.params.get("state") == "absent":

        if installed_version is None:
            return {
                "changed": False,
                "msg": "NCPA is not installed, no changes needed."
            }

        if module.check_mode:
            return {
                "changed": True,
                "msg": "NCPA {0} is installed, it would be uninstalled".format(installed_version)
            }

        rc, stdout, stderr = remove_ncpa(module,paths)

        if rc != 0 or get_installed_ncpa_version(module, paths) is not None:
            return {
                "failed": True,
                "changed": False,
                "msg": "ERROR: Failed to uninstall NCPA",
                "stderr": stderr
            }

        return {
            "changed": True,
            "msg": "Uninstalled NCPA"
        }

    else:
        return {
            "failed": True,
            "changed": False,
            "msg": f"ERROR: Unknown state type: {module.params.get('state')}"
        }