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
			async with session.get(url=f'http://{domain}/{suffix}/?sdeasdefsa', headers=HEADERS) as response:
				resp = await response.text()

				if 'rastrear su paquete' in resp.lower() or 'Descargar aplicación' in resp:
					break

				reply = html.fromstring(reply)
				link = reply.xpath("//a[starts-with(@href, 'http')]")[0]

				return link.attrib['href']
		except Exception as e:
			pass

	print(f'Ignoring {domain}')
	return None


async def check_hosts(domains, suffixes):
	timeout = aiohttp.ClientTimeout(total=60)

	async with aiohttp.ClientSession(timeout=timeout) as session:
		ret = await asyncio.gather(*(_check_host(domain, suffixes, session) for domain in domains))

	return [r for r in ret if ret]


if __name__ == '__main__':
	with open(os.path.join(os.getcwd(), 'filters', 'fedex.yml')) as f:
		data = yaml.safe_load(f)
		domains = data['domains']
		suffixes = data['fedex_suffixes']

	start = time.time()
	links = asyncio.run(check_hosts(domains, suffixes))
	end = time.time()

	print("Took {} seconds to check {} domains.".format(end - start, len(domains)))

	# for link in links:
	# 	parsed_link = urlsplit(link)

	# 	if not re.match(r'^[a-z0-9]{80,}$', parsed_link.query):
	# 		print('WARNING - NEW LINK FORMAT!?: ' + link)
	# 		continue

	# 	new_domain = parsed_link.netloc
	# 	if new_domain.startswith('www.'):
	# 		new_domain = new_domain[4:]

	# 	if new_domain in domains:
	# 		print('Nothing new!')
	# 	else:
	# 		print('yay')

	with open(os.path.join(os.getcwd(), 'filters', 'fedex.yml'), 'w') as f:
		f.write("# Don't bother manually updating this file.\n")
		f.write("# It is automatically updated with the tools/update-fedex-list.py script.\n")
		yaml.dump({'domains': sorted(domains), 'fedex-suffixes': sorted(suffixes)}, f)
