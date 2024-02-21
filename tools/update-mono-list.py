#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True

import requests
import yaml
from publicsuffixlist import PublicSuffixList
import os


if __name__ == '__main__':
	psl = PublicSuffixList()
	filter_file = os.path.join(os.getcwd(), 'filters', 'mono.yml')
	extra_hosts = set()

	with open(filter_file) as f:
		saved_data = yaml.safe_load(f)
		known_domains = set(saved_data['domains'])

	vault_reply = requests.get('https://otx.alienvault.com/otxapi/indicator/IPv4/passive_dns/134.209.136.68').json()

	for entry in vault_reply['passive_dns']:
		if not entry['whitelisted']:
			hostname = entry['hostname']
			known_domains.add(psl.privatesuffix(hostname))

			if hostname not in known_domains:
				extra_hosts.add(hostname)

	with open(filter_file, 'w') as f:
		f.write("# Don't bother manually updating this file.\n")
		f.write("# It is automatically updated with the tools/update-mono-list.py script.\n")
		yaml.dump({'domains': sorted(known_domains), 'extra_hosts': sorted(extra_hosts)}, f)
