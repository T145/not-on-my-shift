
import inspect
import pkgutil
import sys

# Adapted from https://stackoverflow.com/a/8556471/4454028
def iter_classes(dirname):
	for importer, package_name, _ in pkgutil.iter_modules([dirname]):
		module = importer.find_module(package_name).load_module(package_name)
		for name, cls in inspect.getmembers(module, lambda x: inspect.isclass(x) and x.__module__ == module.__name__):
			yield cls
