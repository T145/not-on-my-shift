#!/usr/bin/env python3

import requests
import time
import lxml.html
import random
import sys
import adutil
import os
import yaml
import re
from urllib.parse import urlsplit

print('Begin')

class NotHostingException(Exception):
	pass

with open(os.path.join(os.getcwd(), 'filters', 'fedex.yml')) as f:
	saved_data = yaml.safe_load(f)
	apkhost = saved_data['domains']
	suffixes = saved_data['fedex-suffixes']

checkhosts = set(apkhost)

client = requests.Session()
client.timeout = 5
client.headers['User-Agent'] = 'Mozilla/5.0 (Android 10; Mobile; rv:85.0) Gecko/85.0 Firefox/85.0'

def get_link_for_domain(prev_domain):
	random.shuffle(suffixes)

	for suffix in suffixes:
		print('Trying %s suffix %s' % (prev_domain, suffix))
		reply = client.get('http://' + prev_domain + '/' + suffix + '/?sdeasdefsa').text
		if 'rastrear su paquete' not in reply:
			continue

		reply = lxml.html.fromstring(reply)
		link = reply.xpath("//a[starts-with(@href, 'http')]")[0]
		if 'Descargar aplicación' not in link.text_content():
			continue

		return link.attrib['href']

	return None

def run_iter(prev_domain):
	download_link = get_link_for_domain(prev_domain)
	if download_link is None:
		print('No longer using ' + prev_domain)
		checkhosts.remove(prev_domain)
		return False

	parsed_link = urlsplit(download_link)
	if not re.match(r'^[a-z0-9]{80,}$', parsed_link.query):
		print('WARNING - NEW LINK FORMAT!?: ' + download_link)
		return False

	new_domain = parsed_link.netloc
	if new_domain.startswith('www.'):
		new_domain = new_domain[4:]

	if new_domain not in apkhost:
		link_get = client.get(download_link)
		if link_get.status_code == 200:
			print('New link: ' + download_link)
			
			suffix_match = re.match(r'^/([a-z]+)/$', parsed_link.path)

			if not suffix_match:
				print('WARNING - NEW SUFFIX FORMAT - NOT ADDING TO LIST: ' + download_link)
				return False

			if suffix_match.group(1) not in suffixes:
				print('NEW SUFFIX!: ' + suffix_match.group(1))
				suffixes.append(suffix_match.group(1))
			
			apkhost.append(new_domain)
			checkhosts.add(new_domain)
			return True
		else:
			print('Resolved nonworking link: ' + download_link)
			return False
	else:
		print('Nothing new')
		return False

if __name__ == '__main__':
	try:
		while len(checkhosts) > 0:
			prev_domain = random.choice(list(checkhosts))

			try:
				if run_iter(prev_domain):
					with open(os.path.join(os.getcwd(), 'filters', 'fedex.yml'), 'w') as f:
						f.write("# Don't bother manually updating this file.\n")
						f.write("# It is automatically updated with the tools/update-fedex-list.py script.\n")
						yaml.dump({'domains': sorted(apkhost), 'fedex-suffixes': sorted(suffixes)}, f)
			except Exception as e:
				print('Failed using ' + prev_domain + ': ' + str(e))
				checkhosts.remove(prev_domain)

			time.sleep(10)
	except KeyboardInterrupt:
		pass
