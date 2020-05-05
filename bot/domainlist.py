
class DomainList:
	def __init__(self, file):
		with open(file, 'r') as f:
			self.text = f.read()

	def contains(self, domain):
		domain_regex = r'(^|\n)(#WL:)?' + re.escape(ad_domain) + r'(\n|$)'
		return re.search(ad_domain_regex, self.text) is not None

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
		insert_text = '# %s (auto)\n%s\n' % (ad_url, ad_domain)
		self.text = self.text[:insert_pos] + insert_text + self.text[insert_pos:]
