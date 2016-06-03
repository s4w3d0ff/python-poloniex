from setuptools import setup
import sys
if sys.version_info[0] == 3:
	setup(name='poloniex',
		version='0.1',
		description='Poloniex API wrapper for Python 2.7 and 3',
		url='https://github.com/s4w3d0ff/python-poloniex',
		author='s4w3d0ff',
		license='GPL v2',
		packages=['poloniex'],
		zip_safe=False)
else:
	setup(name='poloniex',
		version='0.1',
		description='Poloniex API wrapper for Python 2.7 and 3',
		url='https://github.com/s4w3d0ff/python-poloniex',
		author='s4w3d0ff',
		license='GPL v2',
		packages=['poloniex'],
		install_requires=['hmac','hashlib'],
		zip_safe=False)
