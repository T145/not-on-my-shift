#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True

import requests
import time
from lxml import html
import random
import os
import yaml
import re
from urllib.parse import urlsplit
import asyncio
import aiohttp


HEADERS = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'
}


async def _check_host(domain, suffixes, session):
	print(f'Testing {domain}')
	random.shuffle(suffixes)

	for suffix in suffixes:
		try:
			async with session.get(url=f'http://{domain}/{suffix}/?sdeasdefsa', headers=HEADERS, allow_redirects=True) as response:
				resp = await response.text()

				if 'rastrear su paquete' in resp.lower() or 'Descargar aplicación' in resp:
					continue

				resp = html.fromstring(resp)
				link = resp.xpath("//a[starts-with(@href, 'http')]")[0]
				link = link.attrib['href']

				# The logic from the original script removed domains:
				# 1) That had no valid link route
				# 2) Whose link query doesn't match the regex r'^[a-z0-9]{80,}$'
				if link:
					parsed_link = urlsplit(link)

					if re.match(r'^[a-z0-9]{80,}$', parsed_link.query):
						domain = parsed_link.netloc

						if domain.startswith('www.'):
							domain = domain[4:]

						return domain
		except Exception as e:
			pass

	print(f'Ignoring {domain}')
	return f'-{domain}'


async def check_hosts(domains, suffixes):
	timeout = aiohttp.ClientTimeout(total=60)

	async with aiohttp.ClientSession(timeout=timeout) as session:
		ret = await asyncio.gather(*(_check_host(domain, suffixes, session) for domain in domains))

	active, inactive = set(), set()

	for host in ret:
		if host:
			if host.startswith('-'):
				inactive.add(host[1:])
			else:
				active.add(host)

	return active, inactive


def load_data(data):
	return set(data) if data else set()


if __name__ == '__main__':
	with open(os.path.join(os.getcwd(), 'filters', 'fedex.yml')) as f:
		data = yaml.safe_load(f)
		domains = load_data(data['domains'])
		suffixes = load_data(data['fedex_suffixes'])
		ignored = load_data(data['ignored_domains'])

	start = time.time()
	domains, ignored = asyncio.run(check_hosts(domains.union(ignored), suffixes))
	end = time.time()

	print("Took {} seconds to check {} domains.".format(end - start, len(domains)))

	with open(os.path.join(os.getcwd(), 'filters', 'fedex.yml'), 'w') as f:
		f.write("# Don't bother manually updating this file.\n")
		f.write("# It is automatically updated with the tools/update-fedex-list.py script.\n")
		yaml.dump({'domains': sorted(domains), 'fedex_suffixes': sorted(suffixes), 'ignored_domains': sorted(ignored_domains)}, f)
