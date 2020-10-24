#!/usr/bin/env python3

import adutil
import requests
import re
import os
import sys
import yaml
import socket
from requests.exceptions import ConnectionError

# Root path of the project
noms_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
print('Project root: %s' % noms_path)

with open(os.path.join(noms_path, 'util', 'prizes-ips.txt')) as f:
	pending_ips = [x.strip() for x in f.read().strip().split()]

prizesdomains = None
with open(os.path.join(noms_path, 'filters.yml')) as f:
	filter_list = yaml.safe_load(f)

known_domains = None
for group in filter_list['groups'].values():
	for entry in group['entries']:
		if entry.get('prizesdomains'):
			known_domains = set(entry['domains'])

if not known_domains:
	print('Could not find current prize domain list', file=sys.stderr)
	sys.exit(1)

print('Previously known: %d' % len(known_domains))

def matches_ad_pattern(x):
	if re.match(r'^[a-z-]{15,30}[0-9]+\.life$', x):
		return True

	if re.search(r'(?:date|dating|prize|bonus).*[1-9-]+', x) and '-' in x and 'update' not in x:
		return True

	return False

pending_domains = set(adutil.list_new_domains())
pending_domains = set(filter(matches_ad_pattern, pending_domains))
pending_domains.update(known_domains)
tested_domains = set(known_domains)
known_ips = set(pending_ips)

while len(pending_ips) > 0 or len(pending_domains) > 0:
	print('=== NEW ITERATION ===')
	print('--- Pending IPs: %d' % len(pending_ips))
	for ip in pending_ips:
		print(' - IP %s' % ip)
		vault_reply = requests.get('https://otx.alienvault.com/otxapi/indicator/IPv4/passive_dns/%s' % ip).json()
		for entry in vault_reply['passive_dns']:
			pending_domains.add(entry['hostname'])
	pending_ips = set()

	# Remove redirection targets
	print('--- Pending domains: %d' % len(pending_domains))
	hostnames = [x for x in sorted(pending_domains) if not x.endswith('.live')]
	for hostname in hostnames:
		hostname = hostname.strip()
		if hostname in tested_domains:
			continue
		tested_domains.add(hostname)

		try:
			print('Test %s' % hostname)
			if adutil.is_prize_domain(hostname):
				known_domains.add(hostname)
				print(hostname)
				for ip in socket.gethostbyname_ex(hostname)[2]:
					if ip not in known_ips:
						print('Adding new IP: %s' % ip)
						pending_ips.add(ip)
						known_ips.add(ip)
		except ConnectionError:
			pass

	pending_domains = set()

print('=== FINAL LIST OF DOMAINS ===')
for domain in sorted(known_domains):
	print('              - %s' % domain)

with open(os.path.join(noms_path, 'util', 'prizes-ips.txt'), 'w') as f:
	for ip in sorted(known_ips):
		print(ip, file=f)
