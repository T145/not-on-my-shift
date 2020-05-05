
from domainscript import DomainScript

class BestPrizesDay2(DomainScript):
	def domain(self):
		return 'bestprizesday2.life'

	def iterate(self):
		found = self.get_and_match(
				'https://bestprizesday2.life/?u=tqck80z&o=zdqr96x&t=DESKuniqANDsearch',
				r"redirDomain:\['','(https?:\/\/.+?)'"
		)
		yield found

		for e in self.try_numbers_around(found.domain):
			yield e
