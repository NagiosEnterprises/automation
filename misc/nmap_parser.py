#!/usr/bin/python

# this script pulls IP addresses out of a file with nmap XML output
# and then writes the addresses to a different file e.g. ansible host file
# the script assumes the XML file with nmap out put is named nmapxml


import xml.etree.ElementTree as ET
tree = ET.parse(nmapxml)
root = tree.getroot()

with open('writetest', 'a') as f:
    for address in root.iter('address'):
         add = address.get('addr')
         f.write(add + '\n')





