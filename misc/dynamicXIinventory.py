#!/bin/python
import json
import requests

# this statement removes a parsing objection in ansible. By including it we keep the ansible error reporting clean(er).
def verify_file(): pass
verify_file()

# make an api call to XI to retireve hostgroup memebers
hostgroups = requests.get("http://192.168.4.102/nagiosxi/api/v1/objects/hostgroupmembers?apikey=QGOXX34bAbHZG25IWjfreMJCDdoYBFWohLFe4IJT9mSOIdsEv2l445FGhjU8X8Pu&pretty=1")
hosts = requests.get("http://192.168.4.102/nagiosxi/api/v1/objects/host?apikey=QGOXX34bAbHZG25IWjfreMJCDdoYBFWohLFe4IJT9mSOIdsEv2l445FGhjU8X8Pu&pretty=1")

# turn the json into a python object
hostgroups = json.loads(hostgroups.text)
hosts = json.loads(hosts.text)

# create hostgroup dictionary
hostgroup_map = {}
for hg in hostgroups["hostgroup"]:
	if isinstance(hg["members"]["host"], (list)):
		hostgroup_map[hg["hostgroup_name"]] = hg["members"]["host"]
	elif isinstance(hg["members"]["host"], (dict)):
		if hg['members']['host']['host_name']:
			hostgroup_map[hg["hostgroup_name"]] = [hg["members"]["host"]]
		
# create host dictionary
hosts_map = {}
for h in hosts["host"]:
    hosts_map[h["host_name"]] = h["address"]

# begin the build of the json output with groups and hosts
ansible_info = {}
for hg_name in hostgroup_map:
    ansible_info[hg_name] = {
        "hosts": [hosts_map[host['host_name']] for host in hostgroup_map[hg_name]]
    }

# add _meta as required by Ansible
ansible_info.update({"_meta": {"hostvars": {}}})

# add the all group as required by Ansible
host_list = []
for b in hosts_map:
	host_list.append(hosts_map[b])
ansible_info.update({"all": host_list})

# printing the json to stdout creates the inventory list for Ansible
print json.dumps(ansible_info)