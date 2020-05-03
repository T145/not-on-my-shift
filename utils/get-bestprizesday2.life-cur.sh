#!/bin/bash -e
curl -s 'https://bestprizesday2.life/?u=tqck80z&o=zdqr96x&t=DESKuniqANDsearch' \
	-H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0' \
	| sed -nr "s|.*redirDomain:\['','https?://([^/']+).*|\1|p"
