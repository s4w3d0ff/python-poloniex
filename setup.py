from setuptools import setup

read_md = lambda f: open(f, 'r').read()

setup(name='poloniexapi',
      version='0.5.5',
      description='Poloniex API wrapper for Python 2.7 and 3 with websocket support',
      long_description=read_md('README.md'),
      long_description_content_type='text/markdown',
      url='https://github.com/s4w3d0ff/python-poloniex',
      author='s4w3d0ff',
      author_email="info@s4w3d0ff.host",
      license='GPL v2',
      packages=['poloniex'],
      install_requires=['requests', 'websocket_client'],
      zip_safe=False,
      keywords=['poloniex', 'poloniexapi', 'exchange', 'api', 'cryptocoin', 'tradebot', 'polo', 'websocket', 'rest', 'push'],
      classifiers = [
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3'
            ]
      )
