#!/usr/bin/env python3

import adutil
import requests
import yaml
from publicsuffixlist import PublicSuffixList
import os

psl = PublicSuffixList()

filter_file = os.path.join(adutil.project_root, 'filters', 'mono.yml')
with open(filter_file) as f:
	saved_data = yaml.safe_load(f)
	known_domains = set(saved_data['domains'])

vault_reply = requests.get('https://otx.alienvault.com/otxapi/indicator/IPv4/passive_dns/134.209.136.68').json()

for entry in vault_reply['passive_dns']:
	hostname = psl.privatesuffix(entry['hostname'])
	known_domains.add(hostname)

known_domains = sorted(known_domains)
extra_hosts = []

for domain in known_domains:
	for i in range(10):
		extra_hosts.append('%d.%s' % (i, domain))

with open(filter_file, 'w') as f:
	f.write("# Don't bother manually updating this file.\n")
	f.write("# It is automatically updated with the tools/update-mono-list.py script.\n")
	yaml.dump({'domains': known_domains, 'extra_hosts': extra_hosts}, f)
