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


setup(

      name='liten',
      version='0.1.4.0',
      description='a de-duplication command line tool',
      long_description="""
      Liten:  A deduplication command line tool and library
      ===============================================================================

      :Author: Noah Gift
      :Version: $Revision: 0.1.4.0 $
      :Copyright: This document has been placed in the public domain.

      Summary
      ---------

      A deduplication command line tool and library.  A relatively efficient
      algorithm based on filtering like sized bytes, and then performing a full
      md5 checksum, is used to determine duplicate files/file objects.  Files can be deleted upon
      discovery, and pattern matching can be used to limit search results. Finally, configuration file
      use is supported, and there is a developing API that lends itself to customization via an
      ActionsMixin class.



      .. contents::

      Example CLI Usage:
      ------------------


      Size:
      ~~~~~~~~~~~~~~~~~~~~~~

      Search by size using --size or -s option::

      	liten.py -s 1 /mnt/raid         is equal to liten.py -s 1MB /mnt/raid
      	liten.py -s 1bytes /mnt/raid
      	liten.py -s 1KB /mnt/raid
      	liten.py -s 1MB /mnt/raid
      	liten.py -s 1GB /mnt/raid
      	liten.py -s 1TB /mnt/raid

      Report Location:
      ~~~~~~~~~~~~~~~~~~~~~~

      Generate custom report path using -r or --report=/tmp/report.txt::

      	./liten.py --report=/tmp/test.txt /Users/ngift/Documents

      By default a report will be created in CWD, called LitenDuplicateReport.txt.

      Config File:
      ~~~~~~~~~~~~~~~~~~~~~~

      You can use a config file in the following format::

      	[Options]
      	path=/tmp
      	size=1MB
      	pattern=*.m4v
      	delete=True


      You can call the config file anything and place it anywhere.

      Here is an example usage::

      	./liten.py --config=myconfig.ini

      Verbosity:
      ~~~~~~~~~~~~~~~~~~~~~~

      All stdout can be suppressed by using --quiet or -q.

      Delete:
      ~~~~~~~~~~~~~~~~~~~~~~

      By using --delete the duplicate files will be automatically deleted.  The API has support
      for an interactive mode and a dry-run mode, they have not been implemented in the CLI as of yet.

      Example Library/API Usage:
      ~~~~~~~~~~~~~~~~~~~~~~

          >>> Liten = Liten(spath='testData')
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

      There is also the concept of an Action, which can be implemented later, that will allow
      customizable actions to occur upon an a condition that gets defined as you walk down a
      tree of files.

      Tests:
      ~~~~~~~~~~~~~~~~~~~~~~
       * Run Doctests:  ./liten -t or --test
       * Run test_liten.py
       * Run test_create_file.py then delete those test files using liten::
      	python2.5 liten.py --delete /tmp

      Display Options:
      ---------------------------

      Stdout:
      ~~~~~~~~~~~~~~~~~~~~~~
      stdout will show you duplicate file paths and sizes such as::

      	Printing dups over 1 MB using md5 checksum: [SIZE] [ORIG] [DUP]
      	7 MB  Orig:  /Users/ngift/Downloads/bzr-0-2.17.tar
      	Dupe:  /Users/ngift/Downloads/bzr-0-4.17.tar

      Report:
      ~~~~~~~~~~~~~~~~~~~~~~
      A report named LitenDuplicateReport.txt will be created in your current working
      directory::

      	Duplicate Version,     Path,       Size,       ModDate
      	Original, /Users/ngift/Downloads/bzr-0-2.17.tar, 7 MB, 07/10/2007 01:43:12 AM
      	Duplicate, /Users/ngift/Downloads/bzr-0-3.17.tar, 7 MB, 07/10/2007 01:43:27 AM


      Debug Mode Environmental Variables:
      ------------------------------------------------------------------------

      * To enable print statement debugging set LITEN_DEBUG to 1
      * To enable pdb break point debugging set LITEN_DEBUG to 2
      * LITEN_DEBUG_MODE = int(os.environ.get('LITEN_DEBUG', 0))
      * Note:  When DEBUG MODE is enabled, a message will appear to standard out

      QUESTIONS:  noah dot gift at gmail.com
      ------------------------------------------------------

""",
      author='Noah Gift',
      author_email='noah.gift@gmail.com',
      url='http://code.google.com/p/liten/',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      py_modules=['liten'],
      entry_points="""
      [console_scripts]
      liten = liten:main
      """,
      )

