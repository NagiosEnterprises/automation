#!/usr/bin/python

from platform import machine

def parse_os_release():

    os_release = {}

    with open("/etc/os-release", "r") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                os_release[k] = v.strip('"')

    return os_release

def detect_architecture(module):

    arch = machine().lower()

    arch_map = {
        "x86_64": "x86_64",
        "amd64": "x86_64",
        "aarch64": "aarch64",
        "arm64": "aarch64"
    }

    return arch_map.get(arch, arch)

