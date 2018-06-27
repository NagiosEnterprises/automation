#!/bin/bash

####################
# 
# This script will auto-register this host with Nagios XI.
#
####################

##########
#
# Replace the 127.0.0.1 IP address in the line below with the IP address of your Nagios XI server
#
##########

my_xi_serverip=$(127.0.0.1)

##########
#
# Replace this_key in the line below with your actual Nagios XI API key 
#
##########

my_xi_apikey=$(this_key)

##########
#
# The command below stores the IP address of the machine as the variable my_ip
#
# The code is from https://stackoverflow.com/questions/21336126/linux-bash-script-to-extract-ip-address
#
# If you have a more elegant solution you are welcome to use it.
#
# The code shown here uses the Linux ip command, and parses out the ip of this host from the output of the ip command.
# You will notice the ip address 8.8.8.8 for Google's DNS service. In theory, any ip address there ought to work
# as the the command will return the ip address of this host whether the destination ip is reachable or not.
#
##########

my_ip=$(ip route get 8.8.8.8 | awk 'NR==1 {print $NF}')

##########
# 
# The command below stores the hostname of the machine as my_host_name
#
# Uncomment IF you set unique hostnames for your machines AND you want to use this hostname in Nagios XI.
# 
##########

#my_host_name=$(hostname)

##########
#
# The command below is an API call to your Nagios XI instance that will
# create the host with a Nagios Host_name of the ip address of the machine
# 
# Optional edit: change host_name=${my_ip} to host_name=${my_host_name} in the API call below IF you uncommented the
#		$my_host_name=$(hostname) command immediately above this comment block
#
##########

curl -XPOST "http://${my_xi_serverip}/nagiosxi/api/v1/config/host?apikey=${my_xi_apikey}&pretty=1" -d "host_name=${my_ip}&address=${my_ip}&check_command=check_ping\!3000,80%\!5000,100%&max_check_attempts=2&check_period=24x7&contacts=nagiosadmin&notification_interval=5&notification_period=24x7&applyconfig=1"


