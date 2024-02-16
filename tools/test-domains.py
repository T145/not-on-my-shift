#!/usr/bin/env python3

import argparse
from tqdm import tqdm
import socket
import sys
import re
import multiprocessing.pool
import subprocess

FREE_MARKERS = [
	'no match for',
	'status: free',
	'not found',
	'no match',
	'no data found',
	'no entries found',
	'registration status: available',
	'no object found'
]

def domain_exists(domain):
	try:
		socket.gethostbyname(domain)
		return domain, True
	except socket.gaierror as e:
		pass

	wdata = subprocess.run(["whois", domain], capture_output=True)
	stdout = wdata.stdout.decode('ascii', 'ignore').casefold()
	for marker in FREE_MARKERS:
		if marker in stdout:
			return domain, False

	print('Whois for %s tested true but A did not' % domain)
	return domain, True

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Tests which domains in the list exist.')
	parser.add_argument('--file', type=argparse.FileType('r'), default=sys.stdin, help='domain list')
	parser.add_argument('--threads', type=int, default=4, help='domain querying threads')

	args = parser.parse_args()

	domains = set()
	for line in args.file:
		line = line.strip().lower()
		if re.match(r'^([a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)*[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$', line):
			domains.add(line)

	registered = []
	unregistered = []

	with multiprocessing.pool.ThreadPool(args.threads) as pool:
		with tqdm(total=len(domains)) as pbar:
			for domain, result in pool.imap_unordered(domain_exists, domains):
				if result:
					registered.append(domain)
				else:
					unregistered.append(domain)
				pbar.update()

	registered.sort()
	unregistered.sort()

	print('### REGISTERED ###')
	for domain in registered:
		print(domain)

	print()
	print('### UNREGISTERED ###')
	for domain in unregistered:
		print(domain)
