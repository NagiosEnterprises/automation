# Ansible roles for Nagios XI

## Support
The Ansible roles for Nagios XI are a set of community supported roles for affecting changes within the Nagios XI monitoring environment via Ansible.

## Disclaimer
***Please read through each script before attempting to use it in your 
environment.***

These scripts are provided "as is" *without warranty of any kind*, either
expressed or implied, including, but not limited to, the implied warranties
of merchantability and fitness for a particular purpose.

## Installation
The Nagios XI roles should live anywhere you keep roles that you reference in your playbooks.

## Required Ansible Variables
### For both xi_host_scheduled_downtime_create/delete 
- `xi_ip` - The IP address (or hostname) of your Nagios XI server
- `xi_api_key` - The API key for a user on your Nagios XI server
- `downtime_comment` - The comment you want to appear in Nagios XI for the downtime. If running from the commandline, you will be prompted for this variable.
