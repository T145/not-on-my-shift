#!/usr/bin/env python3

import requests
import time
import lxml.html
import random
import sys
import traceback
import adutil
from urllib.parse import urlsplit

assert(len(sys.argv) == 1)

apkhost = adutil.get_domain_group('fedex_domains')
assert(apkhost)

host_valid = list(apkhost)
client = requests.Session()
client.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.68'

while True:
	try:
		prev_domain = random.choice(host_valid)
		reply = client.get('http://' + prev_domain + '/fedex/').text
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

	except Exception as e:
		print('Failed using ' + prev_domain + ': ' + str(e))
		host_valid.remove(prev_domain)

	time.sleep(10)
