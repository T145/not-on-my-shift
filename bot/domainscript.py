
import socket
import re
import requests
import lxml.html
from urllib.parse import urlsplit

class FoundDomain:
	def __init__(self, domain, full_url=None):
		self.domain = domain
		self.full_url = full_url
		self.in_list = None

	@staticmethod
	def for_url(url):
		split_url = urlsplit(url)

		# Domain only
		if split_url.netloc == '':
			return FoundDomain(split_url.path)

		# Domain and URL
		else:
			return FoundDomain(split_url.netloc, url)

class DomainScript:
	def __init__(self, domain_list, sess):
		self.domain_list = domain_list
		self.sess = sess

	def domain(self):
		raise NotImplementedError

	def fetch(self):
		raise NotImplementedError()

	def iterate(self):
		url = self.fetch()
		if url:
			yield FoundDomain.for_url(url)

	def get_and_match(self, url, expression):
		page = self.sess.get(url).text
		matches = re.search(expression, page)
		if matches is None:
			raise Exception('No match found')
		return FoundDomain.for_url(matches.group(1))

	def get_html(self, *args, **kwargs):
		return lxml.html.fromstring(self.sess.get(*args, **kwargs).text)

	def form_data(self, body, selector):
		form = body.xpath(selector)

		if len(form) != 1:
			raise Exception('Found %i elements matching instead of one' % len(form))
		form = form[0]

		return {input.attrib['name']: input.attrib['value'] for input in form.xpath('input')}

	def try_numbers_around(self, domain):
		number_match = re.search('[0-9]+', domain)
		if number_match is None:
			return

		prefix = domain[:number_match.start()]
		orig_num = int(number_match.group(0))
		suffix = domain[number_match.end():]

		cur = orig_num - 1
		while True:
			domain = '%s%i%s' % (prefix, cur, suffix)
			if not self.domain_exists(domain):
				break
			yield FoundDomain(domain)
			cur -= 1

		cur = orig_num + 1
		while True:
			domain = '%s%i%s' % (prefix, cur, suffix)
			if not self.domain_exists(domain):
				break
			yield FoundDomain(domain)
			cur += 1

	def domain_exists(self, domain):
		try:
			socket.gethostbyname(domain)
			return True
		except:
			return False
