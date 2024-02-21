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
from aiohttp.client_exceptions import ClientResponseError


HEADERS = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'
}


async def _check_host(domain, session):
	print(f'Testing {domain}')
	try:
		async with session.get(url=f'http://{domain}/', params={'u': 'tqck80z', 'o': 'zdqr96x', 't': 'DESKuniqANDsearch'}, headers=HEADERS) as response:
			resp = await response.text()

			if 'under construction' in resp.lower() or 'redirDomain' in resp:
				print(f'ACTIVE: {domain}')
				return domain

			return None
	except Exception as e:
		if isinstance(e, ClientResponseError) and (e.status == 400 or e.status == 404):
			print(f'Unable to get {domain}: it will be recorded as dead.')
			return f'-{domain}'
		else:
			print(f'Got recorded offender {domain} with error {e.__class__}.')
			return domain


async def check_hosts(domains):
	timeout = aiohttp.ClientTimeout(total=60)

	async with aiohttp.ClientSession(timeout=timeout) as session:
		ret = await asyncio.gather(*(_check_host(domain, session) for domain in domains))

	active, inactive = set(), set()

	for host in ret:
		if host:
			if host.startswith('-'):
				inactive.add(host[1:])
			else:
				active.add(host)

	return active, inactive


def matches_ad_pattern(x):
	if 'update' in x or x.endswith('.live'):
		return False

	return re.match(r'^[a-z-]{15,30}[0-9]+\.life$', x) or re.search(r'(?:date|dating|prize|bonus).*[1-9-]+', x)


def load_data(data):
	return set(data) if data else set()


if __name__ == '__main__':
	with open(os.path.join(os.getcwd(), 'filters', 'prizes.yml')) as f:
		data = yaml.safe_load(f)
		active_domains = load_data(data['domains'])
		inactive_domains = load_data(data['inactive_domains'])

	print(f'Previously known: {len(active_domains)}')

	with open('nrd-list-downloader/nrd-2days-free.txt') as text:
		pending_domains = set(filter(matches_ad_pattern, set([domain.strip() for domain in text.readlines()])))

	if len(pending_domains) > 0:
		print(f'Pending domains: {len(pending_domains)}')

		pending_domains.union(active_domains)
		pending_domains.union(inactive_domains)

		start = time.time()
		active_hosts, inactive_hosts = asyncio.run(check_hosts(pending_domains))
		end = time.time()

		print("Took {} seconds to check {} domains.".format(end - start, len(pending_domains)))

	with open(os.path.join(os.getcwd(), 'filters', 'prizes.yml'), 'w') as f:
		f.write("# Don't bother manually updating this file.\n")
		f.write("# It is automatically updated with the tools/update-prizes-list.py script.\n")
		yaml.dump({'domains': sorted(active_hosts), 'inactive_domains': sorted(inactive_hosts)}, f)
