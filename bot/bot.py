#!/usr/bin/env python3

import traceback
import http.cookiejar
import lxml.html
import requests
from urllib.parse import urlsplit
from domainlist import DomainList
from moduleiterator import iter_classes

domain_list = DomainList('../domains.txt')

# Cookies are important as each calls returns a new one based on the last served
cookies = http.cookiejar.LWPCookieJar('cookies.txt')
try:
	cookies.load()
except FileNotFoundError:
	pass

sess = requests.Session()
sess.cookies = cookies
sess.headers.update({
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'
})

for cls in iter_classes('scripts'):
	script = cls(domain_list, sess)

	redir_domain = script.domain()
	print('Script: %s' % redir_domain)

	try:
		new_domains = ''
		for found in script.iterate():
			if found.in_list is None:
				found.in_list = domain_list.contains(found.domain)

			if found.in_list:
				print('%s already in list' % found.domain)
				continue

			print('New: %s' % found.domain)
			if found.full_url:
				new_domains += '# %s\n%s\n' % (found.full_url, found.domain)
			else:
				new_domains += '%s\n' % found.domain
	except Exception as e:
		print('Failed to run')
		traceback.print_exc()
		continue

	if new_domains != '':
		domain_list.redirector_append(redir_domain, new_domains)

cookies.save()
domain_list.save()
