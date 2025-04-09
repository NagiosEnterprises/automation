# xi_host_scheduled_downtime_create
---

## *WORK IN PROGRESS*
First, let it be known that this role is a work in progress. This role may not even work at present. Please be patient.

## The Goal
The goal of this role is to create scheduled downtime in Nagios XI for one or more hosts.

## The Use Case
Imagining this being used where Ansible is being used to run OS updates on multiple systems. Ansible, tied in to Nagios XI as its inventory source, can reach back out to Nagios XI and set the hosts into downtime.

## Current Variables
- xi_ip - The IP address of your Nagios XI system
- xi_api_key - The API key used for authenticating to Nagios XI
- downtime_comment - Any comment you would like people to see in the Nagios XI interface related to this downtime
- downtime_start - The start of the scheduled downtime. Usually right around this very instant.
- downtime_end - The end of the scheduled downtime. Usually 2 hours after this very instant.
- inventory_hostname - The hostname of the inventory host currently being processed.

## Other things to note
I have this role delegated to localhost, meaning that the system running Ansible should be the one reaching out to Nagios XI's API. Feeling cute, might make this a variable later. Happy to hear thoughts on the matter.

