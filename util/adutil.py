
import glob
import requests
from zipfile import ZipFile

def list_new_domains():
	all = set()

	for file in glob.iglob('new-domains/*.zip'):
		with ZipFile(file) as zip:
			domains = zip.read('domain-names.txt')
			domains = domains.decode('ascii')
			domains = domains.replace('\r', '')
			domains = domains.split()
			yield from domains

	return all

def is_prize_domain(domain):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'
	}

	# All these domains have a "Under construction" text on the main page, let's use that for fingerprinting
	text_page = requests.get('http://%s/' % domain, headers=headers).text

	if 'Under construction' not in text_page:
		return False

	# They emit a redirect in JS if passed these arguments
	text_page = requests.get('https://%s/?u=tqck80z&o=zdqr96x&t=DESKuniqANDsearch' % domain, headers=headers).text

	if 'redirDomain' not in text_page:
		return False

	return True
