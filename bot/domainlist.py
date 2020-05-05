import re

class DomainList:
	def __init__(self, file):
		self.file = file
		with open(file, 'r') as f:
			self.text = f.read()

	def contains(self, domain):
		domain_regex = r'(^|\n)(#WL:)?' + re.escape(domain) + r'(\n|$)'
		return re.search(domain_regex, self.text) is not None

	def redirector_append(self, redir_domain, text):
		# Find where the redir is listed
		redir_regex = r'(^|\n)' + re.escape(redir_domain) + r'\n'
		match = re.search(redir_regex, self.text)
		assert(match is not None)

		# Find end of paragraph for the redir
		try:
			insert_pos = self.text.index('\n\n', match.end()) + 1
		except ValueError:
			insert_pos = len(self.text)

		# Insert
		self.text = self.text[:insert_pos] + text + self.text[insert_pos:]

	def save(self):
		with open(self.file, 'w') as f:
			f.write(self.text)
