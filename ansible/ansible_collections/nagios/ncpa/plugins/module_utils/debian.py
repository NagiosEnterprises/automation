from ansible_collections.nagios.ncpa.plugins.module_utils.ncpa_common import (
    parse_os_release,
    detect_architecture,
    get_installed_ncpa_version,
    version_satisfied,
    is_nagios_repo_installed,
    ensure_file,
    get_gpg_keys,
    download_file
)

def build_deb_sources(repo_url, keyring):
    return f"""\
Types: deb
URIs: {repo_url}
Suites: /
Signed-By: {keyring}"""

def map_deb_architecture(architecture):
    deb_arch_map = {
        "x86_64": "amd64",
        "amd64": "amd64",
        "aarch64": "arm64",
        "arm64": "arm64",
        "i386": "i386",
        "i686": "i386",
    }
    return deb_arch_map.get(architecture, architecture)

def build_deb_url(version, architecture):
    base_url = "https://assets.nagios.com/downloads/ncpa3"
    architecture = map_deb_architecture(architecture)

    if version in [None, "", "latest"]:
        filename = f"ncpa-latest-1.{architecture}.deb"
    else:
        filename = f"ncpa-{version}-1.{architecture}.deb"

    return f"{base_url}/{filename}"

def remove_ncpa(module,paths):
    return module.run_command(
        [paths["apt"], "remove", "-y", "ncpa"]
    )

def install_deb_prereqs(module):
    """Return None on success, or a failure result dict."""
    rc, stdout, stderr = module.run_command(
                ["apt-get", "install", "gpg", "apt-transport-https", "-y"]
            )

    if rc !=0:
        return {
            "failed": True,
            "changed": False,
            "msg": "ERROR: Failed to install gpg and apt-transport-https",
            "stderr": stderr
        }

    return None

def remove_deb_repo(module,paths):
    rc, stdout, stderr = module.run_command(
        [paths["apt"], "remove", "-y", "nagios-repo"]
    )

    if rc != 0:
        return {
            "changed": False,
            "msg": "Ran into error",
            "stderr": stderr
        }

    return rc == 0

def handle_deb(module):
    changed = False
    paths = {
        "apt": module.get_bin_path("apt-get"),
        "dpkg_query": module.get_bin_path("dpkg-query")
    }

    if not paths["apt"] or not paths["dpkg_query"]:
        return {
            "failed": True,
            "changed": False,
            "msg": "ERROR: apt-get or dpkg-query was not found on this host."
        }

    version = module.params.get("version")
    package_source = module.params.get("package_source")
    installed_version = get_installed_ncpa_version(module, paths)
    satisfied = version_satisfied(installed_version, version)

    if module.params.get("state") == "present":

        if module.check_mode is True:
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

        architecture = detect_architecture(module)

        if package_source == "package":

            if satisfied:
                return {
                    "changed": False,
                    "msg": "NCPA {0} is already installed".format(installed_version),
                    "installed_version": installed_version
                }

            url = build_deb_url(
                version,
                architecture
            )

            if not url:
                return {
                    "failed": True,
                    "changed": changed,
                    "msg": "ERROR: Failed to build URL"
                }

            tmp_deb = "/tmp/ncpa.deb"
            try:
                download_file(url, tmp_deb)
            except Exception as e:
                return {
                    "failed": True,
                    "changed": changed,
                    "msg": "ERROR: Failed to download NCPA package from {0}".format(url),
                    "stderr": str(e)
                }

            cmd = [
                paths["apt"],
                "-y",
                "install",
                tmp_deb
            ]

            rc, stdout, stderr = module.run_command(cmd)

            if rc !=0:
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
                        "ERROR: apt reported success, but the installed NCPA "
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

            os_release = parse_os_release()

            repo_url = (
                "https://repo.nagios.com/deb/{}".format(os_release["VERSION_CODENAME"])
            )

            prereq_error = install_deb_prereqs(module)
            if prereq_error:
                return prereq_error

            desired_content = build_deb_sources(repo_url, "/usr/share/keyrings/nagios.gpg")

            if ensure_file(module,"/etc/apt/sources.list.d/nagios.sources", desired_content):
                changed = True

            desired_content = get_gpg_keys()

            key_changed = ensure_file(module, "/tmp/GPG-KEY-NAGIOS-V3", "{}".format(desired_content["v3"]))

            if key_changed:
                changed = True

                # Properly install GPG key (--batch --yes: overwrite an existing keyring non-interactively)
                rc, stdout, stderr = module.run_command(
                    ["gpg", "--batch", "--yes", "--dearmor", "-o", "/usr/share/keyrings/nagios.gpg", "/tmp/GPG-KEY-NAGIOS-V3"]
                )

                if rc != 0:
                    return {
                        "failed": True,
                        "changed": changed,
                        "msg": "ERROR: Failed to --dearmor Nagios GPG key",
                        "stderr": stderr
                    }

            if satisfied:
                return {
                    "changed": changed,
                    "msg": "NCPA {0} is already installed".format(installed_version),
                    "installed_version": installed_version
                }

            # Update repo
            rc, stdout, stderr = module.run_command(
                ["apt-get", "update"]
            )

            if rc != 0:
                return {
                    "failed": True,
                    "changed": changed,
                    "msg": "ERROR: apt-get update failed",
                    "stderr": stderr
                }

            # Install NCPA
            rc, stdout, stderr = module.run_command(
                ["apt-get", "install", "-y", "ncpa"]
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
                    "msg": "ERROR: apt reported success, but NCPA is not installed"
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
                "msg": "NCPA {0} is installed, it would be uninstalled.".format(installed_version)
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
