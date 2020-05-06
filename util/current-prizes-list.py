#!/usr/bin/env python3

import sys
import requests
import json
import socket
import glob
import re
from zipfile import ZipFile

ips = [
	'5.188.178.19',
	#'5.188.178.180',
	#'5.188.178.120',
	#'62.138.18.107',
	#'85.25.210.155',
]

printed = set()

def test_all(hostnames):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'
	}

	hostnames = sorted(hostnames)
	for hostname in hostnames:
		hostname = hostname.strip()

		if hostname in printed:
			continue

		# All these domains have a "Under construction" text on the main page, let's use that for fingerprinting
		try:
			text_page = requests.get('http://%s/' % hostname).text
		except:
			continue

		if 'Under construction' not in text_page:
			continue

		# They emit a redirect in JS if passed these arguments
		try:
			text_page = requests.get('https://%s/?u=tqck80z&o=zdqr96x&t=DESKuniqANDsearch' % hostname, headers=headers).text
		except:
			continue

		if 'redirDomain' not in text_page:
			continue

		if hostname not in printed:
			printed.add(hostname)
			print(hostname)

for ip in ips:
	print('# IP %s' % ip)
	vault_reply = requests.get('https://otx.alienvault.com/otxapi/indicator/IPv4/passive_dns/%s' % ip).json()
	test_all([entry['hostname'] for entry in vault_reply['passive_dns']])

recent = set()
for file in glob.iglob('new-domains/*.zip'):
	print(file)
	with ZipFile(file) as zip:
		domains = zip.read('domain-names.txt')
		domains = domains.decode('ascii')

		recent.update(re.findall('^[a-z-]{15,30}[0-9]+\.life', domains, re.MULTILINE))

print('# Recently registered domains matching')
test_all(recent)
