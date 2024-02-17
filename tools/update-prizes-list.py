#!/usr/bin/env python3

import requests
import re
import os
import sys
import socket
import yaml
import csv
import glob
from zipfile import ZipFile
from requests.exceptions import ConnectionError, TooManyRedirects

def matches_ad_pattern(x):
	if re.match(r'^[a-z-]{15,30}[0-9]+\.life$', x):
		return True

	if re.search(r'(?:date|dating|prize|bonus).*[1-9-]+', x) and 'update' not in x:
		return True

	return False

def list_new_domains():
	with open('nrd-list-downloader/nrd-1days-free.txt') as text:
		domains = text.readlines()
		domains = domains.decode('ascii')
		domains = domains.replace('\r', '')
		domains = domains.split()
		yield from domains
	return list()

def _limited_is_prize_domain(domain):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'
	}

	# All these domains have a "Under construction" text on the main page, let's use that for fingerprinting
	text_page = requests.get('http://%s/' % domain, headers=headers).text

	if 'Under construction' not in text_page:
		return False

	# They emit a redirect in JS if passed these arguments
	text_page = requests.get('http://%s/?u=tqck80z&o=zdqr96x&t=DESKuniqANDsearch' % domain, headers=headers, timeout=3).text

	if 'redirDomain' not in text_page:
		return False

	return True

def is_prize_domain(domain):
	try:
		return _limited_is_prize_domain(domain)
	except TimeoutError:
		return False

if __name__ == '__main__':
	with open(os.path.join(os.getcwd(), 'filters', 'prizes.yml')) as f:
		saved_data = yaml.safe_load(f)
		known_domains = set(saved_data['domains'])
		known_ips = set(saved_data['ips'])

	if not known_domains:
		print('Could not find current prize domain list', file=sys.stderr)
		sys.exit(1)

	print('Previously known: %d' % len(known_domains))

	pending_domains = set(list_new_domains())
	print('New domains: %d' % len(pending_domains))
	pending_domains = set(filter(matches_ad_pattern, pending_domains))
	pending_ips = set(known_ips)

	while len(pending_ips) > 0 or len(pending_domains) > 0:
		print('=== NEW ITERATION ===')
		print('--- Pending IPs: %d' % len(pending_ips))
		for ip in pending_ips:
			print(' - IP %s' % ip)
			vault_reply = requests.get('https://otx.alienvault.com/otxapi/indicator/IPv4/passive_dns/%s' % ip).json()
			for entry in vault_reply['passive_dns']:
				hostname = entry['hostname']
				if hostname.startswith('www.'):
					hostname = hostname[4:]
				pending_domains.add(hostname)
		pending_ips = set()

		# Remove redirection targets
		print('--- Pending domains: %d' % len(pending_domains))
		hostnames = [x for x in sorted(pending_domains) if not x.endswith('.live')]
		for hostname in hostnames:
			hostname = hostname.strip()

			try:
				print('Test %s' % hostname)
				if is_prize_domain(hostname):
					known_domains.add(hostname)
					print('NEW: %s' % hostname)
					for ip in socket.gethostbyname_ex(hostname)[2]:
						if ip not in known_ips:
							print('Adding new IP: %s' % ip)
							pending_ips.add(ip)
							known_ips.add(ip)
			except (ConnectionError, TooManyRedirects):
				pass

		pending_domains = set()

	with open(os.path.join(os.getcwd(), 'filters', 'prizes.yml'), 'w') as f:
		f.write("# Don't bother manually updating this file.\n")
		f.write("# It is automatically updated with the tools/update-prizes-list.py script.\n")
		yaml.dump({'domains': sorted(known_domains), 'ips': sorted(known_ips)}, f)
