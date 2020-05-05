#!/usr/bin/env python3

import re
import http.cookiejar
import lxml.html
import requests
from urllib.parse import urlsplit
from moduleiterator import iter_classes

with open('../domains.txt', 'r') as f:
	domains_txt = f.read()

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
	script = cls(sess)

	redir_domain = script.domain()
	print('Script: %s' % redir_domain)

	try:
		ad_url = script.fetch()
	except Exception as e:
		print('Failed to run: %s' % e)
		continue

	if ad_url is None or ad_url == '':
		print('URL could not be determined')
		continue
	print('Found URL is %s' % ad_url)

	ad_domain = urlsplit(ad_url).netloc
	if ad_domain == '':
		print('Could not determine domain for %s' % repr(ad_url))
		continue

	ad_domain_regex = r'(^|\n)(#WL:)?' + re.escape(ad_domain) + r'\n'
	if re.search(ad_domain_regex, domains_txt):
		print('Domain already in white/blacklist')
		continue

	# Find where the redir is listed
	redir_regex = r'(^|\n)' + re.escape(redir_domain) + r'\n'
	match = re.search(redir_regex, domains_txt)
	assert(match is not None)

	# Find end of paragraph for the redir
	try:
		insert_pos = domains_txt.index('\n\n', match.end())
	except ValueError:
		insert_pos = len(domains_txt)

	# Insert
	insert_text = '# %s (auto)\n%s\n' % (ad_url, ad_domain)
	domains_txt = domains_txt[:insert_pos] + insert_text + domains_txt[insert_pos:]

cookies.save()

print(domains_txt)
