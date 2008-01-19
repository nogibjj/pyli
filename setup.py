#!/usr/bin/env python

# liten 0.1.3 -- deduplication command line tool
#
# Author: Noah Gift
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


setup(

      name='liten',
      version='0.1.3',
      description='a de-duplication command line tool',
      long_description="""
      Liten
======

* Command Line Tool and Library To Eliminate Duplicates and Facilitate Intelligent Merging of Data\
Structures

* Liten is in very active development

Example CLI Usage
---------------------------------

These are some example usage scenarios::
    
    >liten.py -s 1 /mnt/raid 
    >liten.py -s 1bytes /mnt/raid 
    >liten.py -s 1MB /mnt/raid
    >liten.py -s 1GB /mnt/raid
    >liten.py -s 1TB /mnt/raid

Example Library Usage
---------------------------------

These are some example usage scenarios::

    >>> Liten = LitenBaseClass(spath='testData')
    >>> dupeFileOne = 'testData/testDocOne.txt'
    >>> checksumOne = Liten.createChecksum(dupeFileOne)
    >>> dupeFileTwo = 'testData/testDocTwo.txt'
    >>> checksumTwo = Liten.createChecksum(dupeFileTwo)
    >>> nonDupeFile = 'testData/testDocThree_wrong_match.txt'
    >>> checksumThree = Liten.createChecksum(nonDupeFile)
    >>> checksumOne == checksumTwo
    True
    >>> checksumOne == checksumThree
    False


Development Status
---------------

* Liten is in very active development, and stable, but it should still be considered alpha.
* 0.1.3 is the current stable release.
* 0.1.4 is the next planned release and it should include a --destructive and --dry-run option\
for deleting duplicates from a directory.  This future release may also include the ability to inspect\
tar file and other archives for duplicates, as well as cache/pickle queries to speed up searches.

Download and Installation
-------------------------

Liten can be installed with `Easy Install
<http://peak.telecommunity.com/DevCenter/EasyInstall>`_ by typing::

    > easy_install liten

RPMS and Debian packages should be available soon.  You can also view all available packages including\
source from <http://code.google.com/p/liten/>

Bugs
-------------------------
* Bug Reporting:  https://launchpad.net/liten
* Questions:  Noah Gift/noah.gift@gmail.com

"""















author='Noah Gift',
      author_email='noah.gift@gmail.com',
      url='http://code.google.com/p/liten/',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      py_modules=['liten']
      entry_points="""
      [console_scripts]
      liten = liten:main
      """,
      )

