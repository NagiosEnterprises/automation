from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: nagiosxi
    plugin_type: inventory
    short_description: Returns Ansible inventory from a Nagios XI system
    description: Returns Ansible inventory from a Nagios XI system
    options:
        plugin:
            description: Name of the plugin
            required: True
            choices: ['nagiosxi']
        disable_warnings:
            description: Disable TLS checks for https connections to Nagios XI's API
            required: True
            choices: ['True', 'False']
        secure:
            description: Whether to use http or https. If False, http, if True, https.
            required: True
            choices: ['True', 'False']
        xi_ip:
            description: The IP or hostname of the Nagios XI system.
            required: True
        xi_api_key:
            description: The API key capable of reading the Nagios XI API
            required: True
        xi_hostgroup:
            description: The Hostgroup containing hosts you want to manage with Ansible
            required: True
'''
EXAMPLES = '''
plugin: nagiosxi
disable_warnings: "True"
secure: "False"
xi_ip: 192.168.0.20
xi_api_key: th0XBK6EiR9aJsg26ipq8CevPhLYPYlK3rnD2dqd6OFa6eb48
xi_hostgroup: AnsibleManaged
'''

import requests
import sys
import os

from ansible import constants as C
from ansible.errors import AnsibleParserError, AnsibleParserError
from ansible.module_utils.common.text.converters import to_native, to_text
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable

class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):

    NAME = 'nagiosxi'
    _load_name = 'nagiosxi'

    def _empty_inventory():
        returnempty = self.inventory_header()

        return returnempty

    def __init__(self):

        self.secure = None
        self.xiurl = None
        self.xiapikey = None
        self.xihostgroup = None

        super(InventoryModule, self).__init__()

        #self.xiurl = self.get_option('xiurl')
        #self.xiapikey = self.get_option('xiapikey')
        #self.xihostgroup = self.get_option('xihostgroup')

        #if self.get_option('disable_warnings') == 'True':
        #    requests.packages.urllib3.disable_warnings()



    def inventory_header(self):
        inv_headers = {}
        inv_headers['_meta'] = { 'hostvars': {} }

        return inv_headers

    def verify_file(self, path):

        valid = False
        if super(InventoryModule, self).verify_file(path):
            file_name, ext = os.path.splitext(path)

            if not ext or ext in C.YAML_FILENAME_EXTENSIONS:
                valid = True

        return valid

    def parse(self, inventory, loader, path, cache=True):

        super(InventoryModule, self).parse(inventory, loader, path, cache=cache)

        self._read_config_data(path)

        try:
            self.xiurl = self.get_option('xi_ip')
            self.xiapikey = self.get_option('xi_api_key')
            self.xihostgroup = self.get_option('xi_hostgroup')

            if self.get_option('disable_warnings') == 'True':
                requests.packages.urllib3.disable_warnings()

            if self.get_option('secure') == 'True':
                self.xiurl = 'https://{0}/nagiosxi/api/v1/'.format(self.xiurl)
            else:
                self.xiurl = 'http://{0}/nagiosxi/api/v1/'.format(self.xiurl)


        except Exception as e:
            raise AnsibleParseError(
                    'All correct options required: {}'.format(e))

        self._populate()



    def _populate(self):
        hostsfromnagios = self.inventory_header()
        managedhostsurl = self.xiurl + 'objects/hostgroupmembers?apikey={0}&hostgroup_name={1}&pretty=0'.format(self.xiapikey,self.xihostgroup)
        managedhosts = requests.get(managedhostsurl, verify=False)

        for host in managedhosts.json()['hostgroup'][0]['members']['host']:
            hostdetailsurl = self.xiurl + 'objects/host?apikey={0}&host_name={1}&customvars=1&pretty=0'.format(self.xiapikey,host['host_name'])

            groupdetailurl = self.xiurl + 'config/host?apikey={0}&host_name={1}&pretty=0'.format(self.xiapikey,host['host_name'])

            #Grab host variables
            hostdetail = requests.get(hostdetailsurl, verify=False).json()

            #Grab additional hostgroup membership and put a new entry into hostsfromnagios
            groupdetail = requests.get(groupdetailurl, verify=False).json()

            for group in groupdetail[0]['hostgroups']:
                if group not in self.inventory.get_groups_dict():
                    self.inventory.add_group(group)

                self.inventory.add_host(host=hostdetail['host'][0]['address'], group=group)

            for var, value in hostdetail['host'][0]['customvars'].items():
                self.inventory.set_variable(hostdetail['host'][0]['address'], var.lower(), value)

                #This will add the host to the Ansible host group.
            #    hostsfromnagios[group]['hosts'].append(hostdetail['host'][0]['address'])

        #return hostsfromnagios


    def verifyhostgroupname(self):
        validcharacters = list(string.ascii_lowercase)
        validcharacters.extend(list(string.ascii_uppercase))
        validcharacters.extend(list(range(0,10,1)))
        validcharacters.extend('_')
        invalidchars = []

        for char in list(self.xi_hostgroup):
            if char not in validcharacters:
                invalidchars.append(char)

        if len(invalidchars) > 0:
            sys.exit("Ansible will not accept, or has difficulty dealing with the following characters: {0}".format(invalidchars))
        else:
            return True

    def gethosts(self):
        try:
            response = requests.get(self.url)
        except ConnectionError as e:
            raise SystemExit(e)

        if 'error' in response.json():
            e = "Error connecting to the API. Response was: {0}".format(response.json()['error'])
            return False

        return response

    def sorthosts(self, hostlist: requests.models.Response):
        for host in hostlist.json():
            if xi_hostgroup in host['hostgroup']:
                pass
