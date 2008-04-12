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

version = '0.1.4.2'
f = open(os.path.join(os.path.dirname(__file__), 'docs', 'index.txt'))
long_description = f.read().strip()
f.close()

setup(

      name='liten',
      version='0.1.4.2',
      description='a de-duplication command line tool',
      long_description=long_description,
      classifiers=[
              'Development Status :: 4 - Beta',
              'Intended Audience :: Developers',
              'License :: OSI Approved :: MIT License',
            ],
      author='Noah Gift',
      author_email='noah.gift@gmail.com',
      url='http://pypi.python.org/pypi/liten',
      download_url="http://code.google.com/p/liten/downloads/list",
      license='MIT',
      py_modules=['virtualenv'],
      zip_safe=False,
      py_modules=['liten'],
      entry_points="""
      [console_scripts]
      liten = liten:main
      """,
      )

