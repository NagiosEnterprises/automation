# xi_host_scheduled_downtime_delete
---

## *WORK IN PROGRESS*
First, let it be known that this role is a work in progress. This role may not even work at present. Please be patient.

## The Goal
The goal of this role is to delete scheduled downtime in Nagios XI for one or more hosts.

## The Use Case
Imagining this being used where Ansible is being used to run OS updates on multiple systems. Assuming that the updates were run within the downtime window, this role could be used to remove existing downtime. 

## Current Variables
- xi_ip - The IP address of your Nagios XI system
- xi_api_key - The API key used for authenticating to Nagios XI
- inventory_hostname - The hostname of the inventory host currently being processed.
- downtime_result - The role queries the Nagios XI API for the downtime related to the current inventory host, then deletes the downtime.

## Other things to note
I have this role delegated to localhost, meaning that the system running Ansible should be the one reaching out to Nagios XI's API. Feeling cute, might make this a variable later. Happy to hear thoughts on the matter.

If you read the `downtime_result` variable description and thought, "Wait...What happens if there's more than 1 scheduled downtime entry for a given host," good catch! I don't know yet. I'm in the middle of 8 different things, all of which are irritating. But I will find out, and find a better way to make sure that we're destroying the appropriate downtime entry.