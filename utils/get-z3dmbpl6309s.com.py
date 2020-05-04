#!/usr/bin/env python3

import requests
import lxml.html
import http.cookiejar

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

page = sess.get('http://z3dmbpl6309s.com/kcj93ej3j?key=0f22c1fd609f13cb7947c8cabfe1a90d&submetric=8025').text
page = lxml.html.fromstring(page)

form_data = {input.attrib['name']: input.attrib['value'] for input in page.xpath('//form[@id="submit-form"]/input')}
form_data['in'] = 'false'

redir = sess.get('http://z3dmbpl6309s.com/kcj93ej3j', params=form_data, allow_redirects=False)
assert(redir.status_code in (301, 302))
print(redir.headers['Location'])

cookies.save()
