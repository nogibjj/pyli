#!/usr/bin/env python

# liten 0.1.4 -- deduplication command line tool
#
# Author: Noah Gift
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
import os,sys

version = '0.1.4.0'
f = open(os.path.join(os.path.dirname(__file__), 'docs', 'index.txt'))
long_description = f.read().strip()
f.close()

setup(

      name='liten',
      version='0.1.4.0',
      description='a de-duplication command line tool',
      long_description=long_description,
      classifiers=[
              'Development Status :: 4 - Beta',
              'Intended Audience :: Developers',
              'License :: OSI Approved :: MIT License',
            ],
      keyword='liten cli deduplication',
      author='Noah Gift',
      author_email='noah.gift@gmail.com',
      url='http://pypi.python.org/pypi/liten',
      license='MIT',
      py_modules=['virtualenv'],
      zip_safe=False,
      py_modules=['liten'],
      ## Hacks to get the package data installed:
      #copied from ian bicking.
      packages=[''],
      package_dir={'': '.'},
      #package_data={'': ['support-files/*-py%s.egg' % sys.version[:3]]},
      zip_safe=False,
      entry_points="""
      [console_scripts]
      liten = liten:main
      """,
      )

