#!/usr/bin/env python3

import adutil
import requests
import re

ips = [
	'5.188.178.19',
	'5.188.178.180',
	'5.188.178.120',
	'62.138.18.107',
	'85.25.210.155',
	'193.35.50.251',
]

printed = set()

def test_all(hostnames):
	# Remove redirection targets
	hostnames = [x for x in hostnames if not x.endswith('.live')]

	hostnames = sorted(hostnames)
	for hostname in hostnames:
		hostname = hostname.strip()
		if hostname in printed:
			continue

		try:
			if adutil.is_prize_domain(hostname):
				printed.add(hostname)
				print(hostname)
		except Exception:
			pass

for ip in ips:
	print('# IP %s' % ip)
	vault_reply = requests.get('https://otx.alienvault.com/otxapi/indicator/IPv4/passive_dns/%s' % ip).json()
	test_all([entry['hostname'] for entry in vault_reply['passive_dns']])

def matches_ad_pattern(x):
	if re.match(r'^[a-z-]{15,30}[0-9]+\.life$', x):
		return True

	if re.search(r'(?:date|dating).*[1-9]+', x) and '-' in x and 'update' not in x:
		return True

	return False

recent = set(adutil.list_new_domains())
recent = filter(matches_ad_pattern, recent)

print('# Recently registered domains matching')
test_all(recent)
