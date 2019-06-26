import glob
import os
import subprocess

from distutils.core import Command
from setuptools import setup, find_packages

subprocess.call(
    ('mkdir -p aws_scripts/data && '
     'git describe --tags --dirty > aws_scripts/data/ver.tmp '
     '&& mv aws_scripts/data/ver.tmp aws_scripts/data/ver '
     '|| rm -f aws_scripts/data/ver.tmp'),
    shell=True, stderr=open(os.devnull, "w"))

from aws_scripts import __version__


class CheckVersion(Command):
    description = 'Confirm that the stored package version is correct'
    user_options = []

    def run(self):
        with open('aws_scripts/data/ver') as f:
            stored_version = f.read().strip()

        git_version = subprocess.check_output(
            ['git', 'describe', '--tags', '--dirty']).strip()

        assert stored_version == git_version
        print('the current version is', stored_version)


package_data = ['data/*']

params = {'author': 'Sheena Todhunter',
          'author_email': 'sheena.todhunter@gmail.com',
          'description': 'Scripts to push data to AWS',
          'name': 'aws_scripts',
          'packages': find_packages(),
          'package_dir': {'aws_scripts': 'aws_scripts'},
          'entry_points': {
              'console_scripts': ['aws = aws_scripts.scripts.main:main']
          },
          'version': __version__,
          'package_data': {'aws_scripts': package_data},
          'test_suite': 'tests',
          'cmdclass': {'check_version': CheckVersion}
          }

setup(**params)

