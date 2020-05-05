
import re
import requests
import lxml.html

class DomainScript:
	def __init__(self, sess):
		self.sess = sess

	def domain(self):
		raise NotImplementedError

	def fetch(self):
		raise NotImplementedError()

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
