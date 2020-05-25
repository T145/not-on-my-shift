#!/usr/bin/env python3

import argparse
from publicsuffixlist import PublicSuffixList
import re
import textwrap
from urllib.parse import urlsplit
import yaml

parser = argparse.ArgumentParser(description='Converts Yaml filters to hosts and ABP.')
parser.add_argument('yaml', type=argparse.FileType('r'), help='input Yaml file')
parser.add_argument('--hosts', type=argparse.FileType('w'), help='output hosts file')
parser.add_argument('--domains', type=argparse.FileType('w'), help='output domains file')
parser.add_argument('--abp', type=argparse.FileType('w'), help='output ABP file')
args = parser.parse_args()

psl = PublicSuffixList()
filters_by_type = yaml.safe_load(args.yaml)

def get_plural(entry, singular, fallback=None):
	plural = '%ss' % singular
	if singular in entry:
		if plural in entry:
			raise Exception('Found both %s and %s in %s' % (singular, plural, repr(entry)))
		return [entry[singular]]
	return entry.get(plural, fallback)

def remove_prefix(text, prefix):
	if text.startswith(prefix):
		return text[len(prefix):]
	return text

for type_name, type_group in filters_by_type.items():
	group_header = type_group['header']
	printed_abp_header = False
	printed_domains_header = False
	printed_hosts_header = False

	for entry in type_group['entries']:
		date = entry.get('date', '????-??-??')
		description = entry.get('desc', '').strip()
		domains = get_plural(entry, 'domain')
		filters = get_plural(entry, 'filter')
		hosts = get_plural(entry, 'host')
		samples = get_plural(entry, 'sample', [])

		# Step 1: extract domains from samples if no filters, hosts or domains have been specified

		if domains is None and filters is None and hosts is None:
			domains = [remove_prefix(urlsplit(sample).netloc, 'www.') for sample in samples]

		# Step 2: domains to hosts and filters

		if filters is None:
			filters = ['||%s^' % domain for domain in domains]

		if domains is not None:
			hosts = hosts or list()
			for domain in domains:
				hosts.append(domain)

				# Add www if TLD
				if psl.privatesuffix(domain) == domain:
					hosts.append('www.%s' % domain)
		else:
			if hosts is not None:
				raise Exception('Entry has hosts but no domains: %s' % repr(entry))

		# Step 3: autogenerate filters for mail beacons
		if type_name == 'mail_beacons':
			# TODO
			pass

		# Step 4: generate comment
		comment = str(entry.get('date'))

		if description:
			# If single line, put next to date - else put in next lines
			if '\n' not in description:
				comment += ' ' + description
			else:
				comment += '\n' + description
		comment += '\n'

		if samples:
			if '\n' in description:
				comment += '\n'
			for sample in samples:
				comment += ' - %s\n' % sample

		# Step 5: write entries
		if args.abp and filters:
			if not printed_abp_header:
				args.abp.write(textwrap.indent(group_header, '! '))
				args.abp.write('\n')
				printed_abp_header = True

			args.abp.write(textwrap.indent(comment, '! '))
			for filter in filters:
				print(filter, file=args.abp)
			args.abp.write('\n')

		if args.domains and domains:
			if not printed_domains_header:
				args.domains.write(textwrap.indent(group_header, '# '))
				args.domains.write('\n')
				printed_domains_header = True

			args.domains.write(textwrap.indent(comment, '# '))
			for domain in domains:
				print(domain, file=args.domains)
			args.domains.write('\n')

		if args.hosts and hosts:
			if not printed_hosts_header:
				args.hosts.write(textwrap.indent(group_header, '# '))
				args.hosts.write('\n')
				printed_hosts_header = True

			args.hosts.write(textwrap.indent(comment, '# '))
			for host in hosts:
				print('0.0.0.0 ' + host, file=args.hosts)
			args.hosts.write('\n')
