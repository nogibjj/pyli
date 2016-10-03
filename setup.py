#!/usr/bin/env python

from os.path import dirname,join
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

f = open(join(dirname(__file__), 'docs', 'index.txt'))
long_description = f.read().strip()
f.close()

setup(
      name='liten',
      version='0.1.6',
      description='a de-duplication command line tool',
      long_description=long_description,
      classifiers=[
              'Development Status :: 4 - Beta',
              'Intended Audience :: Developers',
              'License :: OSI Approved :: MIT License',
            ],
      author='Noah Gift',
      author_email='noah.gift@gmail.com',
      url='https://github.com/nogibjj/pyli',
      download_url="https://github.com/nogibjj/pyli",
      license='MIT',
      zip_safe=False,
      py_modules=['liten', 'test_liten'],
      entry_points="""
      [console_scripts]
      liten = liten:main
      """,
      )
