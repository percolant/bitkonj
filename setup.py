from setuptools import setup, find_packages

setup(
  name='bitkonj',
  packages=find_packages(include=['src', 'src.*']),
  package_dir={'': 'src'},
  install_requires=[
    'aiogram',
    'aiohttp',
    'sqlalchemy',
    'sqlalchemy-utils',
    'requests'
  ],
  entry_points={
    'console_scripts': [
        'bitkonj=bitkonj.bitkonj:main',
    ],
  }
)
