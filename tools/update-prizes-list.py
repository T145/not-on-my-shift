#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True

import requests
import re
import os
import socket
import yaml
import glob
import asyncio
import aiohttp
import time


HEADERS = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'
}


async def get(domain, session):
	print('Testing %s' % domain)
	try:
		async with session.get(url=f'http://{domain}/', params={'u': 'tqck80z', 'o': 'zdqr96x', 't': 'DESKuniqANDsearch'}, headers=HEADERS) as response:
			resp = await response.text()
			#print("Successfully got url {} with resp of length {}.".format(url, len(resp)))
			if 'under construction' in resp.lower() or 'redirDomain' in resp:
				print(f'NEW: {domain}')
				return domain
	except Exception as e:
		print("Unable to get {} due to {}.".format(domain, e.__class__))
		return None


async def main(domains):
	timeout = aiohttp.ClientTimeout(total=60)
	async with aiohttp.ClientSession(timeout=timeout) as session:
		ret = await asyncio.gather(*(get(domain, session) for domain in domains))
	return [r for r in ret if r is not None]


def matches_ad_pattern(x):
	if re.match(r'^[a-z-]{15,30}[0-9]+\.life$', x):
		return True

	if re.search(r'(?:date|dating|prize|bonus).*[1-9-]+', x) and 'update' not in x:
		return True

	return False


def list_new_domains():
	with open('nrd-list-downloader/nrd-1days-free.txt') as text:
		return [domain.strip() for domain in text.readlines()]
	return list()


if __name__ == '__main__':
	with open(os.path.join(os.getcwd(), 'filters', 'prizes.yml')) as f:
		data = yaml.safe_load(f)
		known_domains = data['domains']
		known_ips = data['ips']

	if not known_domains:
		print('Could not find current prize domain list', file=sys.stderr)
		sys.exit(1)

	print(f'Previously known: {len(known_domains)}')
	pending_domains = set(filter(matches_ad_pattern, set(list_new_domains())))
	print(f'Recent domains: {len(pending_domains)}')
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
				pending_domains.add(hostname.strip())
		pending_ips = set()

		# Remove redirection targets
		print(f'--- Pending domains: {len(pending_domains)}')

		hostnames = [x for x in sorted(pending_domains) if not x.endswith('.live')]

		start = time.time()
		hostnames = asyncio.run(main(hostnames))
		known_domains.extend(hostnames)
		end = time.time()

		print("Took {} seconds to check {} domains.".format(end - start, len(hostnames)))

		for hostname in hostnames:
			try:
				for ip in socket.gethostbyname_ex(hostname)[2]:
					if ip not in known_ips:
						print('Adding new IP: %s' % ip)
						pending_ips.add(ip)
						known_ips.add(ip)
			except:
				pass

		pending_domains = set()

	with open(os.path.join(os.getcwd(), 'filters', 'prizes.yml'), 'w') as f:
		f.write("# Don't bother manually updating this file.\n")
		f.write("# It is automatically updated with the tools/update-prizes-list.py script.\n")
		yaml.dump({'domains': sorted(known_domains), 'ips': sorted(known_ips)}, f)
