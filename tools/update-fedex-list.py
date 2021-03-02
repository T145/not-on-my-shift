#!/usr/bin/env python3

import requests
import time
import lxml.html
import random
import sys
import adutil
import os
import yaml
from urllib.parse import urlsplit
from kill_timeout import kill_timeout

print('Begin')

class NotHostingException(Exception):
	pass

with open(os.path.join(adutil.project_root, 'filters', 'fedex.yml')) as f:
	saved_data = yaml.safe_load(f)
	apkhost = saved_data['domains']

suffixes = ['web', 'pkg', 'app', 'fedex']
client = requests.Session()
client.timeout = 5
client.headers['User-Agent'] = 'Mozilla/5.0 (Android 10; Mobile; rv:85.0) Gecko/85.0 Firefox/85.0'

@kill_timeout(20)
def get_link_for_domain(prev_domain):
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
		raise NotHostingException('Domain ' + prev_domain + ' no longer hosting')

	parsed_link = urlsplit(download_link)

	new_domain = parsed_link.netloc
	if new_domain.startswith('www.'):
		new_domain = new_domain[4:]

	if new_domain not in apkhost:
		link_get = client.get(download_link)
		if link_get.status_code == 200:
			print('New link: ' + download_link)
			apkhost.append(new_domain)
		else:
			print('Resolved nonworking link: ' + download_link)
	else:
		print('Nothing new')

try:
	while len(apkhost) > 0:
		prev_domain = random.choice(apkhost)
		try:
			run_iter(prev_domain)

		except NotHostingException as e:
			print('No longer using ' + prev_domain)
			apkhost.remove(prev_domain)

		except Exception as e:
			print('Failed using ' + prev_domain + ': ' + str(e))

		time.sleep(10)
except KeyboardInterrupt:
	pass
