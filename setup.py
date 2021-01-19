from setuptools import setup, find_packages

setup(
  name='bitkonj',
  version='0.0.1',
  description='Bitkonj',
  py_modules=['bitkonj'],
  packages=find_packages(include=['src', 'src.*']),
  package_dir={'': 'src'},
  install_requires=[
    'aiogram',
    'aiohttp',
    'sqlalchemy',
    'sqlalchemy-utils',
    'requests',
    'typing_extensions'
  ],
  entry_points={
    'console_scripts': [
        'bitkonj=bitkonj.bitkonj:main',
    ],
  }
)
