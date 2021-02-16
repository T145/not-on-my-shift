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
		domain = random.choice(host_valid)
		reply = client.get('http://' + domain + '/fedex/').text
		reply = lxml.html.fromstring(reply)
		link = reply.xpath("//a[starts-with(@href, 'http')]")[0].attrib['href']
		parsed_link = urlsplit(link)
		if parsed_link.netloc not in apkhost:
			print(parsed_link.netloc)
			apkhost.add(parsed_link.netloc)
			host_valid.append(parsed_link.netloc)
	except Exception as e:
		print('Failed using ' + domain + ': ' + str(e))
		host_valid.remove(domain)

	time.sleep(10)
