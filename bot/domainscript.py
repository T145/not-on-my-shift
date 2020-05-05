
import re
import requests
import lxml.html
from urllib.parse import urlsplit
from collections import namedtuple

FoundDomain = namedtuple('FoundDomain', ('domain', 'full_url'))

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
		split_url = urlsplit(url)

		# Domain only
		if split_url.netloc == '':
			if not self.domain_list.contains(split_url.path):
				yield FoundDomain(split_url.path, None)

		# Domain and URL
		else:
			if not self.domain_list.contains(split_url.netloc):
				yield FoundDomain(split_url.netloc, url)

	def get_and_match(self, url, expression):
		page = self.sess.get(url).text
		matches = re.search(expression, page)
		if matches is None:
			raise Exception('No match found')
		return matches.group(1)

	def get_html(self, *args, **kwargs):
		return lxml.html.fromstring(self.sess.get(*args, **kwargs).text)

	def form_data(self, body, selector):
		form = body.xpath(selector)

		if len(form) != 1:
			raise Exception('Found %i elements matching instead of one' % len(form))
		form = form[0]

		return {input.attrib['name']: input.attrib['value'] for input in form.xpath('input')}
