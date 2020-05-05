
from domainscript import DomainScript

class Z3dmbpl6309s(DomainScript):
	def domain(self):
		return 'z3dmbpl6309s.com'

	def fetch(self):
		page = self.get_html('http://z3dmbpl6309s.com/kcj93ej3j?key=0f22c1fd609f13cb7947c8cabfe1a90d&submetric=8025')
		form_data = self.form_data(page, '//form[@id="submit-form"]')
		form_data['in'] = 'false'
		return self.sess.get('http://z3dmbpl6309s.com/kcj93ej3j', params=form_data, allow_redirects=False).headers['Location']
