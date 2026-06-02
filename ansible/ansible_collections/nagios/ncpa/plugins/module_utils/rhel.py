
from ansible_collections.nagios.ncpa.plugins.module_utils.ncpa_common import (
    parse_os_release,
    detect_architecture,
    is_ncpa_installed
)

def is_nagios_repo_installed(module):
    # I should make this one more generic and throw it into common, as well.

    rc, stdout, stderr = module.run_command(
        ["ls", "/etc/yum.repos.d/nagios*"]
    )

    return rc == 0

def get_install_ncpa_version(module,rpm_path):
    return {
        "changed": False,
        "msg": f"ERROR: get_install_ncpa_version() not implemented yet."
    }

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
    paths = {
        "rpm": module.get_bin_path("rpm"),
        "dnf": module.get_bin_path("dnf")
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
        major_release = parse_os_release()
        architecture = detect_architecture(module)
        
        if module.params.get("package_source") == "package":
            url = build_rpm_url(
                version,
                major_release["VERSION"],
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
            
            os_release = parse_os_release()
            repo_dash_map = {
                "8": 2,
                "9": 2,
                "10": 1
            }
            repo_dash_num = repo_dash_map[os_release['VERSION_ID']]

            repo_url = (
                f"https://repo.nagios.com/nagios/"
                f"{os_release['VERSION_ID']}/"
                f"nagios-repo-{os_release['VERSION_ID']}"
                f"-{repo_dash_num}.el{os_release['VERSION_ID']}.noarch.rpm"
            )

            if not is_nagios_repo_installed(module):
                    rc, stdout, stderr = module.run_command(
                        [paths["rpm"], 
                        "-Uvh", 
                        repo_url]
                    )

                    if rc != 0:
                        return {
                            "changed": changed,
                            "msg": f"Failed to install the nagios-repo rpm, URL {repo_url}",
                            "stderr": stderr
                        }

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

      
         

      # Check to see what installation method to use

      # Install NCPA
        
