from ansible_collections.nagios.ncpa.plugins.module_utils.ncpa_common import (
    parse_os_release,
    detect_architecture,
    is_ncpa_installed,
    ensure_file,
    get_gpg_keys
)

def build_deb_sources(repo_url, keyring):
    return f"""\
Types: deb
URIs: {repo_url}
Suites: /
Signed-By: {keyring}"""

def build_deb_url(version, architecture):
    base_url = "https://assets.nagios.com/downloads/ncpa3"

    if version in [None, "", "latest"]:
        filename = f"ncpa-latest-1.{architecture}.deb"
    else:
        filename = f"ncpa-{version}-1.{architecture}.deb"
    
    return f"{base_url}/{filename}"

def remove_ncpa(module,paths):
    rc, stdout, stderr = module.run_command(
        [paths["apt-get"], "remove", "-y", "ncpa"]
    )

    if rc != 0:
        return {
            "changed": False,
            "msg": "Ran into error",
            "stderr": stderr
        }
    
    return rc == 0

def install_deb_prereqs(module):
    rc, stdout, stderr = module.run_command(
                ["apt-get", "install", "gpg", "apt-transport-https", "-y"]
            )

    if rc !=0:
        return {
            "changed": False,
            "msg": "ERROR: Failed to install gpg and apt-transport-https",
            "stderr": stderr
        }
    
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
        "apt": module.get_bin_path("apt-get")
    }

    installed = is_ncpa_installed(module, paths["apt"])

    if module.params.get("state") == "present":
        
        if module.check_mode is True:
            if installed is True:
                return {
                    "changed": False,
                    "msg": "NCPA is already installed, no changes would be made."
                }
            else:
                return {
                    "changed": True,
                    "msg": "NCPA is not installed, it would be installed."
                }
        
        version = module.params.get("version")
        architecture = detect_architecture(module)

        if module.params.get("package_source") == "package":
            url = build_deb_url(
                version,
                architecture
            )

            if not url:
                return {
                    "changed": changed,
                    "msg": "ERROR: Failed to build URL"
                }
            
            cmd = [
                paths["apt"],
                "-y",
                "install",
                url
            ]

            rc, stdout, stderr = module.run_command(cmd)

            if rc !=0:
                return {
                    "changed": changed,
                    "msg": "ERROR: Failed to install NCPA",
                    "stderr": stderr
                }
            
            changed = True

            return {
                "changed": changed,
                "msg": "NCPA installed successfully"
            }
        
        elif module.params.get("package_source") == "repository":
        
            os_release = parse_os_release()

            repo_url = (
                "https://repo.nagios.com/deb/{}".format(os_release["VERSION_CODENAME"])
            )
            
            desired_content = build_deb_sources(repo_url, "/usr/share/keyrings/nagios.gpg")

            changed = ensure_file(module,"/etc/apt/sources.list.d/nagios.sources", desired_content)

            install_deb_prereqs(module)

            desired_content = get_gpg_keys()

            changed = ensure_file(module, "/tmp/GPG-KEY-NAGIOS-V3", "{}".format(desired_content["v3"]))
            
            if changed is True:

                # Properly install GPG key
                rc, stdout, stderr = module.run_command(
                    ["gpg", "--dearmor", "-o", "/usr/share/keyrings/nagios.gpg", "/tmp/GPG-KEY-NAGIOS-V3"]
                )

                if rc != 0:
                    return {
                        "changed": changed,
                        "msg": "ERROR: Failed to --dearmor Nagios GPG key",
                        "stderr": stderr
                    }
            
            # Update repo
            rc, stdout, stderr = module.run_command(
                ["apt-get", "update"]
            )

            # Install NCPA
            rc, stdout, stderr = module.run_command(
                ["apt-get", "install", "ncpa"]
            )

            if rc != 0:
                return {
                    "changed": changed,
                    "msg": "ERROR: Failed to install NCPA",
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
                return {
                    "changed": False,
                    "msg": "NCPA is not installed, no changes would be made."
                }
            else:
                return {
                    "changed": True,
                    "msg": "NCPA is installed, it would be uninstalled."
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

