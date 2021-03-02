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

with open(os.path.join(adutil.project_root, 'filters', 'fedex.yml')) as f:
	saved_data = yaml.safe_load(f)
	apkhost = set(saved_data['domains'])

host_valid = list(apkhost)
client = requests.Session()
client.headers['User-Agent'] = 'Mozilla/5.0 (Android 10; Mobile; rv:85.0) Gecko/85.0 Firefox/85.0'

try:
	while True:
		try:
			prev_domain = random.choice(host_valid)
			reply = client.get('http://' + prev_domain + '/pkg/').text
			reply = lxml.html.fromstring(reply)
			link = reply.xpath("//a[starts-with(@href, 'http')]")[0].attrib['href']
			parsed_link = urlsplit(link)

			new_domain = parsed_link.netloc
			if new_domain.startswith('www.'):
				new_domain = new_domain[4:]

			if new_domain not in apkhost:
				print(new_domain)
				apkhost.add(new_domain)
				host_valid.append(new_domain)

				with open(os.path.join(adutil.project_root, 'filters', 'prizedomains.yml'), 'w') as f:
					f.write("# Don't bother manually updating this file.\n")
					f.write("# It is automatically updated with the tools/update-fedex-list.py script.\n")
					yaml.dump({'domains': sorted(apkhost)}, f)

		except Exception as e:
			print('Failed using ' + prev_domain + ': ' + str(e))
			host_valid.remove(prev_domain)

		time.sleep(10)
except KeyboardInterrupt:
	pass
