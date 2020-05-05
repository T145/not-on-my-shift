#!/usr/bin/env python3

import sys
import requests
import json
import socket

def domain_exist(domain):
	try:
		socket.gethostbyname(domain)
		return True
	except:
		return False

assert(len(sys.argv) == 2)
ip = sys.argv[1]

for entry in requests.get('https://otx.alienvault.com/otxapi/indicator/IPv4/passive_dns/%s' % ip).json()['passive_dns']:
	hostname = entry['hostname']
	if domain_exist(hostname):
		print(hostname)

