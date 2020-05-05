
from domainscript import DomainScript
import re

class BestPrizesDay2(DomainScript):
	def domain(self):
		return 'bestprizesday2.life'

	def iterate(self):
		base_url = self.get_and_match(
				'https://bestprizesday2.life/?u=tqck80z&o=zdqr96x&t=DESKuniqANDsearch',
				r"redirDomain:\['','(https?:\/\/.+?)'"
		)
		

