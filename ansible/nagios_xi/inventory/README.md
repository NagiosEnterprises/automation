# Nagios XI Dynamic Inventory Plugin

## Support
The Nagios XI Dynamic Inventory Plugin is a community supported plugin for pulling hosts, host groups, and host custom variables from Nagios XI. The plugin will then translate these items into hosts, host groups, and host facts for use with Ansible.

## Installation
The `nagiosxi.py` file should live in your home directory, under `~/.ansible/plugins/inventory/nagiosxi/`

## User Created Inventory File
Create an inventory file with the following fields:

```
plugin: nagiosxi

disable_warnings: False
xi_ip: <IP Address of Nagios XI>
secure: True
xi_api_key: <ReallyReallyLongAPIKey>
xi_hostgroup: AnsibleManaged
```

`plugin` This field tells Ansible what inventory plugin to use. This should be the same name as the directory in `~/.ansible/plugins/inventory/` in this case, `nagiosxi`.

`disable_warnings` This field will determine whether or not Python-related warnings will be disabled or not. Specifically for warnings like HTTPS servers with self-signed certificates.

`xi_ip` This should be the IP address, or hostname, of your Nagios XI server.

`secure` Determines whether Python will use HTTP or HTTPS to connect to your Nagios XI server.

`xi_api_key` This is a key generated for a user in your Nagios XI system. Currently, the user _must_ be an Admin user. Making them a user and giving them full permissions. We highly recommend creating a service account for this, rather than using someone's actual API key.

`xi_hostgroup` This is a hostgroup defined inside of Nagios XI. In the example, we are using AnsibleManaged as our starting hostgroup.

## Making the Nagios XI Dynamic Inventory Plugin useful
This section is all about things you will want to know about in order to help use Nagios XI as your inventory source.

### Hostgroups
Number one is going to be hostgroups. In Nagios XI, a hostgroup is a logical grouping of hosts. Pretty simple. Normally hostgroups are used to group up hosts that make sense to be grouped together in some way. Usually these are things like Linux server vs Windows servers, database servers vs application servers, or maybe datacentera vs datacenterb.

Ansible has its own host group system, and it just so happens to line up quite nicely with Nagios XI. So when the dynamic inventory plugin pulls hosts from Nagios XI, one of the things it will grab is the hostgroup information from each of the hosts. This lets you expand Nagios hostgroups into areas that are useful for Ansible.

A hostgroup in Nagios XI can be created by going to the Core Configuration Manager (CCM) -> Selecting Host Groups -> and clicking the Add New button.

A host can be added to a hostgroup in two different ways. You can assign the hostgroup to the host, or the host to the hostgroup. I'm going to make a unilateral decision here, and give you the directions for the former, because that's what I like to do, and it will make a little more sense when we discuss Templates a little further down.

First go to the Core Configuration Manager (CCM) -> Select Hosts -> Select a host you would like to add to a hostgroup -> Click the Manage Host Groups button. Select any hostgroups you want this host to be a member of, click Add Selected, and then Close.

#### Hostgroups Example 1
As an example, you might have prodhosts vs testhosts as hostgroups in Nagios XI. Any hosts in XI that are pulled by the dynamic inventory plugin will also read whether the hosts are members of prodhosts or testhosts. This could allow you to apply Windows updates to your testing environment to see how well they will roll out, before sending them on to production hosts.

In my own use case, I put all of my hosts into the AnsibleManaged hostgroup in Nagios XI, and then determine which groups I want to run playbooks against after the fact. However, for larger environments, that may not be a good idea.

#### Hostgroups Example 2
Let's say, for example, that you have a large environment, of maybe 400-500 servers and devices that you're monitoring regularly. But then you also have a dynamically scalable application that you host for your customers. In this case you might have two AnsibleManaged type hostgroups. One for your regular servers and devices, and one specifically for your dynamic application.

In doing this, you could then have two Ansible inventory files. One which starts at the hostgroup for your regular servers and devices, and one that only looks at the systems in your dynamic application.

### Custom Variables
This is the lesser known feature of Nagios XI. But in similar fashion to hostgroups in Nagios XI, and host groups in Ansible, there is an amazing opportunity to pair Nagios XI custom variables with Ansible's host variables. This dynamic inventory plugin will help you take advantage of that pairing.

In Nagios XI, custom variables can be defined at the host level, or the service level. Since we're working with Ansible's inventory, let's focus on host custom variables. In order to define a host custom variable in Nagios XI, go to the Core Configuration Manager (CCM) -> Click on Hosts -> Select a host you would like to add a variable to and click on it -> Click on the Misc Settings tab -> And then click the Manage Custom Variables button.

Now you should have a window where you can add as many custom variables as you like. Note that custom variables need to start with an underscore ( _ ). Let's start by creating a custom variable that Ansible can use. In the `name` field, enter `_ansible_private_key_file` and for the value enter a path where there is an SSH key file that Ansible could use for SSH'ing into another host. For my example, I have, `/home/ansibelle/ansible/keys/id_ed25519`. *Please take special note, we are specifying the private key file, here.*

As long as you're here, you can also define `_ansible_user` as a custom variable as well.

These variables will show up on your Ansible system when you run `ansible-inventory --graph my_xi_inventory.yml`, assuming your inventory file is named `my_xi_inventory.yml`, of course.

#### Potentialy Useful Custom Variables
The three easy variables that come to mind are:
`_ansible_user`
`_ansible_connection`
`_ansible_private_key_file`

With these three variables, you can define what user to use to connect to a given system, how Ansible should go about connecting to it, and if the connection method is SSH, where Ansible can find the right private key file to use.

But, if your connection method is WinRM, what then? Well, replace `_ansible_private_key_file` with `_ansible_password`. With WinRM, you'll also need an additional variable, which is the transport. `_ansible_winrm_transport`

One other thing to consider is any variable you might use in your roles. Maybe you have a variable defined on your Nagios XI hosts that an Ansible `when` clause will evaluate.

### Templates
Strictly speaking, Nagios XI templates won't help the integration with XI and Ansible, so much as they will help you manage hostgroups and custom variables in Nagios XI. Looking back at one of our examples, we talked about having four or five hundred devices to monitor. You really don't want to have to micromanage which hosts get which custom variables, and which hosts are members of which hostgroups.

That's where templating comes into play. You can define multiple hostgroups, and custom variables in a single template, and then just apply that template to your variaous hosts. It will save you a ton of time.

To create a new template in Nagios XI, go to the Core Configuration Manager (CCM) -> Select Templates -> In the left menu, under Templates, select Host Templates -> Click the Add New button. The page you are brought to looks very much like a host definition page. So managing hostgroups, and custom variables will be similar to what you've done previously. The Manage Host Groups button can be found in the Common Settings tab, and the Manage Custom Variables button can be found under the Misc Settings tab.
