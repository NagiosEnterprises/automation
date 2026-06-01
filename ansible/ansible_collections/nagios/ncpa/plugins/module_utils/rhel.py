
from ansible_collections.nagios.ncpa.plugins.module_utils.ncpa_common import (
    parse_os_release,
    detect_architecture
)

def is_ncpa_installed(module,rpm_path):

    rc, stdout, stderr = module.run_command(
        [rpm_path, "-q", "ncpa"]
    )
    
    if rc == 0:
        return True
    else:
        return False

def is_nagios_repo_installed(module):

    rc, stdout, stderr = module.run_command(
        ["ls", "/etc/yum.repos.d/nagios*"]
    )

    if rc == 0:
        return True
    else:
        return False

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
    pass

def remove_rhel_repo(module,paths):
    pass


def handle_rhel(module):

    paths = {
        "rpm": module.get_bin_path("rpm"),
        "dnf": module.get_bin_path("dnf")
    }

    installed = is_ncpa_installed(module,paths["rpm"])

    if module.params.get("state") == "present":
        
        if installed is True:
            if module.check_mode:
                # Exit saying NCPA is already installed, no changes would be made.
                return {
                    "changed": False,
                    "msg": "NCPA would not install, as it is already installed"
                }
            else:
                # Exit saying NCPA is already installed
                return {
                    "chnaged": False,
                    "msg": "NCPA is already installed"
                }
        
        else:
            changed = False

            version = module.params.get("version")
            major_release = parse_os_release()
            architecture = detect_architecture(module)
            
            if module.params.get("install_method") == "package":
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
            elif module.params.get("install_method") == "repository":
                return {
                    "changed": False,
                    "msg": "Repository installation not implemented yet. It's supposed to be installed next Tuesday."
                }
            else:
                return {
                    "changed": False,
                    "msg": f"ERROR: Unknown install_method {module.params.get('install_method')}"
                }

    elif module.params.get("state") == "absent":
        pass
    else:
        return {
            "changed": False,
            "msg": f"ERROR: Unknown state type: {module.params.get('state')}"
        }

      
         

      # Check to see what installation method to use

      # Install NCPA
        
