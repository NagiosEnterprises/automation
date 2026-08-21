from ansible_collections.nagios.ncpa.plugins.module_utils.ncpa_common import (
    parse_os_release,
    detect_architecture,
    is_ncpa_installed,
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
    rc, stdout, stderr = module.run_command(
        [paths["dnf"], "remove", "-y", "ncpa"]
    )

    if rc != 0:
        return {
            "changed": False,
            "msg": "Ran into error",
            "stderr": stderr
        }

    return rc == 0

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
            "changed": False,
            "msg": "ERROR: Neither dnf nor yum was found on this host."
        }

    installed = is_ncpa_installed(module,paths["rpm"])

    if module.params.get("state") == "present":

        if module.check_mode:
            if installed is True:
                return {
                    "changed": False,
                    "msg": "NCPA is already installed, no changes would be made."
                }
            else:
                return {
                    "changed": True,
                    "msg": "NCPA is not installed, it would be installed"
                }


        version = module.params.get("version")
        os_release = parse_os_release()
        major_release = get_os_major_version(os_release)
        architecture = detect_architecture(module)

        if module.params.get("package_source") == "package":
            url = build_rpm_url(
                version,
                major_release,
                architecture
            )

            if not url:
                return {
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
                    "changed": changed,
                    "msg": "ERROR: Failed to install NCPA",
                    "stderr": stderr
                }

            changed = True

            return {
                "changed": changed,
                "msg":"NCPA installed successfully"
            }
        elif module.params.get("package_source") == "repository":

            repo_dash_map = {
                "8": 2,
                "9": 2,
                "10": 1
            }
            repo_dash_num = repo_dash_map.get(major_release)
            if repo_dash_num is None:
                return {
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
                        "changed": changed,
                        "msg": f"Failed to install the nagios-repo rpm, URL {repo_url}",
                        "stderr": stderr
                    }
                changed = True

            if is_ncpa_installed(module,paths["rpm"]):
                return {
                    "changed": changed,
                    "msg": "NCPA is already installed"
                }

            rc, stdout, stderr = module.run_command(
                [paths["rpm"], "--import", "https://repo.nagios.com/GPG-KEY-NAGIOS-V2"]
            )

            if rc != 0:
                return {
                    "changed": changed,
                    "msg": "ERROR: Failed to add Nagios repo key V2",
                    "stderr": stderr
                }

            rc = ""
            stdout = ""
            stderr = ""

            rc, stdout, stderr = module.run_command(
                [paths["rpm"], "--import", "https://repo.nagios.com/GPG-KEY-NAGIOS-V3"]
            )

            if rc != 0:
                return {
                    "changed": changed,
                    "msg": "ERROR: Failed to add Nagios repo key v3",
                    "stderr": stderr
                }

            rc = ""
            stdout = ""
            stderr = ""

            rc, stdout, stderr = module.run_command(
                [paths["dnf"], "install", "-y", "ncpa"]
            )

            if rc != 0:
                return {
                    "changed": changed,
                    "msg": "Failed to install NCPA",
                    "stderr": stderr
                }

            rc = ""
            stdout = ""
            stderr = ""

            rc, stdout, stderr = module.run_command(
                ["systemctl", "enable", "ncpa"]
            )

            if rc != 0:
                return {
                    "changed": changed,
                    "msg": "Failed to set NCPA to start on boot",
                    "stderr": stderr
                }

            changed = True

            return {
                "changed": changed,
                "msg": "Nagios repository, and NCPA installed successfully."
            }

        else:
            return {
                "changed": False,
                "msg": f"ERROR: Unknown package_source {module.params.get('package_source')}"
            }

    elif module.params.get("state") == "absent":

        if module.check_mode:
            if installed is False:
                # Exit saying NCPA is not installed, no changes would be made.
                return {
                    "changed": False,
                    "msg": "NCPA is not installed, no changes would be made."
                }
            else:
                return {
                    "changed": True,
                    "msg": "NCPA is installed, it would be uninstalled"
                }

        if remove_ncpa(module,paths):
            return {
                "changed": True,
                "msg": "Uninstalled NCPA"
            }
        else:
            return {
                "changed": False,
                "msg": "ERROR: Failed to uninstall NCPA"
            }


    else:
        return {
            "changed": False,
            "msg": f"ERROR: Unknown state type: {module.params.get('state')}"
        }