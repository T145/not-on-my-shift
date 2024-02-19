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
from aiohttp.client_exceptions import ClientConnectorError


HEADERS = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'
}


async def _check_host(domain, session):
	print('Testing %s' % domain)
	try:
		async with session.get(url=f'http://{domain}/', params={'u': 'tqck80z', 'o': 'zdqr96x', 't': 'DESKuniqANDsearch'}, headers=HEADERS) as response:
			resp = await response.text()

			if 'under construction' in resp.lower() or 'redirDomain' in resp:
				print(f'NEW: {domain}')
				return domain
	except ClientConnectorError as e:
		print("Unable to get {} due to {}: it will be recorded as dead.".format(domain, e.__class__))
		return f'-{domain}'
	except Exception as e:
		print("Unable to get {} due to {}.".format(domain, e.__class__))
		return None


async def check_hosts(domains):
	timeout = aiohttp.ClientTimeout(total=60)

	async with aiohttp.ClientSession(timeout=timeout) as session:
		ret = await asyncio.gather(*(_check_host(domain, session) for domain in domains))

	active, inactive = list(), list()

	for host in ret:
		if host:
			if host.startswith('-'):
				inactive.append(host[1:])
			else:
				active.append(host)

	return active, inactive


def matches_ad_pattern(x):
	if re.match(r'^[a-z-]{15,30}[0-9]+\.life$', x):
		return True

	if 'update' not in x and re.search(r'(?:date|dating|prize|bonus).*[1-9-]+', x):
		return True

	return False


def list_new_domains():
	with open('nrd-list-downloader/nrd-1days-free.txt') as text:
		return [domain.strip() for domain in text.readlines()]
	return list()


if __name__ == '__main__':
	with open(os.path.join(os.getcwd(), 'filters', 'prizes.yml')) as f:
		data = yaml.safe_load(f)
		active_domains = data['active_domains']
		inactive_domains = data['inactive_domains']

	print(f'Previously known: {len(active_domains)}')
	pending_domains = set(filter(matches_ad_pattern, set(list_new_domains())))

	if len(pending_domains) > 0:
		hostnames = [x for x in pending_domains if not x.endswith('.live')]

		print(f'Pending domains: {len(hostnames)}')

		hostnames.extend(active_domains)
		hostnames.extend(inactive_domains)

		start = time.time()
		active_hosts, inactive_hosts = asyncio.run(check_hosts(hostnames))
		active_domains.extend(active_hosts)
		inactive_domains.extend(inactive_hosts)
		end = time.time()

		print("Took {} seconds to check {} domains.".format(end - start, len(hostnames)))

	with open(os.path.join(os.getcwd(), 'filters', 'prizes.yml'), 'w') as f:
		f.write("# Don't bother manually updating this file.\n")
		f.write("# It is automatically updated with the tools/update-prizes-list.py script.\n")
		yaml.dump({'active_domains': sorted(active_domains), 'inactive_domains': sorted(inactive_domains)}, f)
