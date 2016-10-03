#!/usr/bin/env python
#
#  Liten - Deduplication command line tool and library
#
#  Copyright (c) 2007,2008 Noah Gift
#  Copyright (c) 2009,2010 anatoly techtonik
#
#  License:  MIT License
#  http://www.opensource.org/licenses/mit-license.php
#

__version__ = "0.3"
__date__ = "2016-10-02"


__clidoc__ = r"""
Liten:  A deduplication command line tool and library
=====================================================

Summary
---------

Liten determines duplicate files/file objects using relatively efficient
algorithm first selecting like sized files, and then performing a full md5
checksum. Files can be deleted upon discovery, and pattern matching can
be used to limit search scope. Finally, options can be read from
configuration file. There is also unstable development API with behavior
customization via ActionsMixin class.


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
    liten.py c:\in d:\              is equal to liten.py -s 1MB c:\in d:\

Report Location:
~~~~~~~~~~~~~~~~~~~~~~
Path to generate duplication report -r or --report=/tmp/report.txt::

    ./liten.py --report=/tmp/test.txt /Users/ngift/Documents

By default a report is created in current dir as LitenDuplicateReport.csv

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
Screen output can be suppressed by using --quiet or -q.

Delete:
~~~~~~~~~~~~~~~~~~~~~~
By using --delete the duplicate files will be automatically deleted. The API
has support for an interactive mode and a dry-run mode, they have not been
implemented in the CLI as of yet.

Example Library/API Usage:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    >>> Liten = Liten()
    >>> dupeFileOne = 'tests/data/testDocOne.txt'
    >>> checksumOne = Liten.createChecksum(dupeFileOne)
    >>> dupeFileTwo = 'tests/data/testDocTwo.txt'
    >>> checksumTwo = Liten.createChecksum(dupeFileTwo)
    >>> nonDupeFile = 'tests/data/testDocThree_wrong_match.txt'
    >>> checksumThree = Liten.createChecksum(nonDupeFile)
    >>> checksumOne == checksumTwo
    True
    >>> checksumOne == checksumThree
    False

There is also the concept of an Action, which can be implemented later, that
will allow customizable actions to occur upon an a condition that gets
defined as you walk down a tree of files.

Tests:
~~~~~~~~~~~~~~~~~~~~~~
 * Run doctests:  ./liten -t or --test
 * Run tests/test_liten.py
 * Run tests/test_create_file.py then delete those test files using liten::
    python liten.py --delete /tmp

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
By default report LitenDuplicateReport.csv is created in your current
working directory. It is tab separated CSV file::

  Path  Size    ModDate
  /Users/ngift/Downloads/bzr-0-2.17.tar 7 MB    07/10/2007 01:43:12 AM
  /Users/ngift/Downloads/bzr-0-3.17.tar 7 MB    07/10/2007 01:43:27 AM


Debug Mode Environmental Variables:
------------------------------------------------------------------------

* To enable print statement debugging set LITEN_DEBUG to 1
* To enable pdb break point debugging set LITEN_DEBUG to 2
* LITEN_DEBUG_MODE = int(os.environ.get('LITEN_DEBUG', 0))
* Note:  When DEBUG MODE is enabled, a message will appear to standard out

QUESTIONS:  noah dot gift at gmail.com
------------------------------------------------------
"""

import os
import datetime
import re
import sys
import csv
import time
import optparse
import hashlib
import pdb
import configparser
from itertools import chain
from fnmatch import fnmatch

#Liten Debug Mode
#Environmental Variable Options:
#To enable print statement debugging set LITEN_DEBUG to 1
#To enable pdb break point debugging set LITEN_DEBUG to 2

if __debug__:
    LITEN_DEBUG_MODE = int(os.environ.get('LITEN_DEBUG', 0))
    MESSAGE = "LITEN DEBUG MODE ENABLED:"
    if LITEN_DEBUG_MODE == 1:
        print(("%s Print Mode" % MESSAGE))
    if LITEN_DEBUG_MODE == 2:
        print(("%s pdb Mode" % MESSAGE))


class ActionsMixin(object):
    """Subclassable API. Callbacks that Liten calls for actions, i.e. remove()

       Default class does nothing.
    """

    def remove(self, filep, interactive=False, dryrun=False):
        """action to take when file is requested to be removed
        """
        pass

class ActionsAutomatic(ActionsMixin):
    """Process automatically, i.e. remove files"""

    def remove(self, filep, interactive=False, dryrun=False):
        """takes a path and deletes file/unlinks
        """

        #simulation mode for deletion
        if dryrun:
            print(("Dry Run:  %s [NOT DELETED]" % filep))
            return None
        else:
            print(("DELETING:  %s" % filep))
            try:
                status = os.remove(filep)
            except IOError as err:
                print(err)
                return status

class ActionsInteractive(ActionsMixin):
    """Confirm each action interactively"""

    def remove(self, filep, interactive=False, dryrun=False):

        #interactive deletion mode
        if interactive:
            cli_input = input("Do you really want to delete %s [N]/Y" % filep)
            if cli_input == "Y":
                print(("DELETING:  %s" % filep))
                try:
                    status = os.remove(filep)
                except IOError as err:
                    print(err)
                    return status
            elif cli_input == "N":
                print(("Skipping:  %s" % filep))
                return None
            else:
                print(("Skipping:  %s" % filep))
                return None

class FileUtils(object):

    def makeModDate(self, path):
        """
        Makes a modification date object
        """
        mod = time.strftime("%m/%d/%Y %I:%M:%S %p",time.localtime(os.path.getmtime(path)))
        return mod

    def makeCreateDate(self, path):
        """
        Makes a creation date object
        """
        create = time.strftime("%m/%d/%Y %I:%M:%S %p",time.localtime(os.path.getctime(path)))
        return create

    def createChecksum(self, path):
        """
        Reads in file.  Creates checksum of file line by line.
        Returns complete checksum total for file.

        """
        #optional pdb Debug Mode
        if LITEN_DEBUG_MODE == 2:
            pdb.set_trace()

        try:
            fp = open(path)
            checksum = hashlib.md5()
            while True:
                dbuffer = fp.read(8192)
                if not dbuffer:break
                checksum.update(dbuffer)
            fp.close()
            checksum = checksum.digest()
        except IOError:
            print(("IO error for %s" % path))
            checksum = None
            if LITEN_DEBUG_MODE == 1:
                print(('IO error for %s' % path))
        finally:
            if LITEN_DEBUG_MODE:
                print(("Performing checksum on: %s" % path))
        return checksum

    def createSearchDate(self):
        now = datetime.datetime.now()
        date = now.strftime("%Y%m%d")
        return date

    def createExt(self, filep):
        """
        takes a file on a path and returns extension
        """
        (_, ext) = os.path.splitext(filep)
        return ext


class Liten(FileUtils):
    """
    A base class for searching a file tree.

    Contains several methods for analyzing file objects.
    Main method is diskWalker, which walks filesystem and determines
    duplicates.

    You may modify the action that occurs when a duplicate is
    found my subclassing ActionsMixin and specify it as a handler.

    >>> Liten = Liten(spath='testData')
    >>> fakePath = 'tests/data/testDocOne.txt'
    >>> modDate = Liten.makeModDate(fakePath)
    >>> createDate = Liten.makeCreateDate(fakePath)
    >>> dupeFileOne = 'tests/data/testDocOne.txt'
    >>> checksumOne = Liten.createChecksum(dupeFileOne)
    >>> badChecksumAttempt = Liten.createChecksum('fileNotFound.txt')
    IO error for fileNotFound.txt
    >>> dupeFileTwo = 'tests/data/testDocTwo.txt'
    >>> checksumTwo = Liten.createChecksum(dupeFileTwo)
    >>> nonDupeFile = 'tests/data/testDocThree_wrong_match.txt'
    >>> checksumThree = Liten.createChecksum(nonDupeFile)
    >>> checksumOne == checksumTwo
    True
    >>> checksumOne == checksumThree
    False
    >>> SearchDate = Liten.createSearchDate()
    >>> createExt = Liten.createExt(dupeFileOne)
    >>> createExt
    '.txt'

    """
    def __init__(self, spath=None,
                    fileSize='1MB',
                    pattern='*',
                    reportPath="LitenDuplicateReport.csv",
                    config = None,
                    verbose = True,
                    handler = False):

        self.spath = spath
        self.reportPath = reportPath
        self.config = config
        self.fileSize = fileSize
        self.pattern = pattern
        self.verbose = verbose
        #: first checksum only dict
        self.checksum_cache_key = {}
        self.checksum_cache_value = {}
        self.confirmed_dup_key = {}
        self.confirmed_dup_value = {}
        self.byte_cache = {}
        self.matches = []
        if not handler:
            self.handler = ActionsMixin()
        else:
            if not isinstance(handler, ActionsMixin):
                raise TypeError("specified parameter is not ActionsMixin subclass")
            self.handler = handler

        self.dupNumber = 0

    def _cacheChecksum(self, path, checksum, byteSize, filep):

        checksum_cache_value = {'fullPath': path,
                                    'checksum': checksum,
                                    'modDate': self.makeCreateDate(path),
                                    'dupNumber': self.dupNumber,
                                    'searchDate': self.createSearchDate(),
                                    'bytes': byteSize,
                                    'fileType': None,
                                    'fileExt': self.createExt(filep)}

        self.checksum_cache_key[checksum]=checksum_cache_value

    @staticmethod
    def convertSize(sizestr, default='MB'):
        """
        Convert file size from suffixed string to bytes.

        Uses regex search to determine size multiplier.

        :param sizestr: string like '1Mb', '32kb', '2' etc.
        :returns: integer
        :raises: ValueError

        >>> cs = Liten.convertSize
        >>> cs('1kb')
        1024
        >>> cs('233GB')
        250181844992L
        >>> cs('9')
        9437184
        >>> cs('345.5')
        Traceback (most recent call last):
            ...
        ValueError: invalid literal for int() with base 10: '345.5'
        """
        patterns = {'BYTES': 1,
                    'B':  1,
                    'KB': 1024,
                    'MB': 1048576,       # default
                    'GB': 1073741824,
                    'TB': 1099511627776}

        #Detects File Size Type, Strip off Characters
        filesize = sizestr.upper()
        try:
            for key in patterns:
                mult = patterns[key]

                if re.match(r"\d+%s$" % key, filesize):
                    if LITEN_DEBUG_MODE:
                        print(("Sizestr: %s Key: %s Size: %s Multiplier: %s" % \
                               (sizestr, key, filesize, mult)))
                    byteValue = int(filesize.rstrip(key)) * mult
                    break
            else:
                byteValue = int(filesize.strip()) * patterns[default]
        except ValueError as err:
            if LITEN_DEBUG_MODE:
                print(("Problem evaluating:", sizestr, Exception, err))
            raise
        return byteValue

    def diskWalker(self):
        """Walks Directory Tree Looking at Every File, while performing a
        duplicate match algorithm.

        Algorithm:
        This divides directory walk into doing either a more informed search
        if byte in key repository, or appending byte_size to list and moving
        to next file.  A md5 checksum is made of any file that has a byte size
        that has been found before.  The checksum is then used as the basis to
        determine duplicates.

        :raises: UnboundLocalError

        >> from liten import Liten
        >>> Liten = Liten(spath='tests', verbose=False)
        >>> Liten.diskWalker()
        {}
        >>> Liten.fileSize="45bytes"
        >>> dupes = Liten.diskWalker()
        >>> print(len(dupes))
        2

        """
        #optional pdb Debug Mode
        if __debug__:
            if LITEN_DEBUG_MODE == 2:
                pdb.set_trace()

        #Local Variables
        report = csv.writer(open(self.reportPath, 'wb'), dialect='excel-tab')
        #  write header
        report.writerow("Path Size ModDate".split())

        if isinstance(self.spath, str):
            main_path = os.walk(self.spath)
        else:
            main_path = chain(*list(map(os.walk, self.spath)))
        try:
            byteSizeThreshold = self.convertSize(self.fileSize)
        except ValueError as err:
            print(err)
            #Note this gets caught using optparse which is cleaner
            raise UnboundLocalError
        if LITEN_DEBUG_MODE == 1:
            print(("File size threshold (in bytes) %s" % byteSizeThreshold))
        self.dupNumber=0
        byte_count=0
        record_count=0

        #times directory walk
        start = time.time()

        if self.verbose:
            print(("Printing dups over %s MB using md5 checksum: \
            [SIZE] [ORIG] [DUP] " % int(byteSizeThreshold/1048576)))

        for root, _, files in main_path:
            for filep in files:
                path = os.path.join(root,filep)      #establishes full path
                if os.path.isfile(path):            #ignores symbolic links
                    byte_size = os.path.getsize(path)
                    #gets number of file examined
                    record_count += 1
                    #File Size, Pattern Filter Section
                    if byte_size >= byteSizeThreshold:
                        if fnmatch(path, self.pattern):         #default * match
                            if LITEN_DEBUG_MODE == 1:
                                print(("Matches: %s" % path))

                            if byte_size not in self.byte_cache:
                                self.byte_cache[byte_size] = {
                                    'path':path,
                                    'checksum':None
                                }

                            else:
                                #size matched, process checksums for a given file size

                                if LITEN_DEBUG_MODE == 1:
                                    print(('Doing checksum on %s' % path))

                                checksum = self.createChecksum(path)

                                if checksum not in self.checksum_cache_key:
                                    orig_path = self.byte_cache[byte_size]['path']
                                    orig_checksum = self.byte_cache[byte_size]['checksum']

                                    if orig_checksum is None:
                                        # save original file checksum in byte cache
                                        orig_checksum = \
                                            self.byte_cache[byte_size]['checksum'] = \
                                                self.createChecksum(orig_path)

                                        # save original file record in a checksum cache
                                        self._cacheChecksum(orig_path, orig_checksum,
                                                                byte_size,
                                                                filep)

                                #now original file checksum is 100% in checksum cache
                                #recheck the condition
                                if checksum not in self.checksum_cache_key:
                                    self._cacheChecksum(path, checksum, byte_size, filep)

                                else: # fill a dupe record
                                    #accumulates bytes of duplicates found
                                    byte_count += byte_size
                                    #accumulates a dupNumber record
                                    self.dupNumber += 1

                                    #since we have a match, creating record with match partner
                                    #and printing match original.
                                    #grab original file path from checksum_cache dict

                                    orig_path = self.checksum_cache_key[checksum]['fullPath']
                                    orig_mod_date = self.checksum_cache_key[checksum]['modDate']
                                    if self.verbose:
                                        print((byte_size/1048576, "MB ", "ORIG: ",\
                                        orig_path, "DUPE: ", path))

                                    #Write separator and original line
                                    report.writerow("")
                                    report.writerow([orig_path,
                                        "%d MB" % (byte_size/1048576), orig_mod_date])

                                    #Gets Duplicates Modification Date
                                    dupeModDate = self.makeCreateDate(path)

                                    #Write duplicate line
                                    report.writerow([path,
                                        "%d MB" % (byte_size/1048576), dupeModDate])

                                    #Execute remove() action from ActionMixin
                                    self.handler.remove(path)

                                    #Note this is a good spot for the dup rec count
                                    self.confirmed_dup_key[orig_path] = self.checksum_cache_value

                                    #setrecord for duplicate match stored
                                    #duplicate code clean up later.
                                    confirmed_dup_value = {'fullPath': path,
                                                            'modDate': dupeModDate,
                                                            'dupNumber': self.dupNumber,
                                                            'searchDate': self.createSearchDate(),
                                                            'checksum': checksum,
                                                            'bytes': byte_size,
                                                            'fileType': None,
                                                            'fileExt': self.createExt(filep)}
                                    self.confirmed_dup_key[path]=confirmed_dup_value


        if self.verbose:
            print ("\n")
            print ("LITEN REPORT: \n")
            print(("Search Path:                 ", self.spath))
            print(("Filtered For Pattern Match:  ", self.pattern))
            if self.config:
                print(("Used config file:            ",self.config))
            print(("Total Files Searched:        ", record_count))
            print(("Wasted Space in Duplicates:  ", byte_count/1048576, " MB"))
            print(("Report Generated at:         ", self.reportPath))
            #get finish time
            end = time.time()
            timer = end - start
            timer = int(timer/60)
            print(("Search Time:                 ", timer, " minutes\n"))

        return  self.confirmed_dup_key   #Note returns a dictionary of all duplicate records

class ProcessConfig(object):
    """
    Reads in optional configuration file that replaces command line options
    """
    def __init__(self, filep="config.ini"):
        self.filep = filep

    def readConfig(self):
        """reads and processes config file and returns results"""

        Config = configparser.ConfigParser()
        Config.read(self.filep)
        sections = Config.sections()
        for parameter in sections:
            #uncomment line below to see how this config file is parsed
            try:
                path = Config.items(parameter)[0][1]
                if LITEN_DEBUG_MODE == 1:
                    print(("Config file path: %s" % path))
            except configparser.Error:
                path = None
            try:
                pattern = Config.items(parameter)[1][1]
                if LITEN_DEBUG_MODE == 1:
                    print(("Config file pattern: %s" % pattern))
            except configparser.Error:
                pattern = None
            try:
                size = Config.items(parameter)[2][1]
                if LITEN_DEBUG_MODE == 1:
                    print(("Config file size: %s" % size))
            except configparser.Error:
                size = None
        return path, size, pattern

class LitenController(object):
    """
    Controller for DiskStat Command Line Tool.
    Handles optionparser parameters and setup.
    """
    def run(self):
        """Run method for Class"""

        #optional pdb Debug Mode
        if __debug__:
            if LITEN_DEBUG_MODE == 2:
                pdb.set_trace()

        descriptionMessage = "A command line tool for detecting duplicates using md5 checksums."

        p = optparse.OptionParser(description=descriptionMessage,
                                    prog='liten',
                                    version='liten %s' % __version__,
                                    usage= '%prog [options] [starting dir1] [dir2] ...')
        p.add_option('--size', '-s',
                    help='minimum file size, example:  10bytes, 10KB, 10MB, 10GB, 10TB '
                    '(no suffix means MB)',
                    default='1MB')
        p.add_option('--pattern', '-p',
                    help='pattern match examples: *.txt, *.iso, music[0-5].mp3',
                    default='*')
        p.add_option('--report', '-r',
                    help='path to store duplicate report (./LitenDuplicateReport.csv by default)',
                    default='LitenDuplicateReport.csv')
        p.add_option('--delete', '-d', action="store_true",
                    help='DELETES all duplicate matches permanently!',default=False)
        p.add_option('--config', '-c', help='specify path to config file')
        p.add_option('--quiet', '-q', action="store_true",
                    help='suppress all screen output except errors',
                    default=False)
        p.add_option('--test', '-t', action="store_true",help='run doctests')

        options, arguments = p.parse_args()

        if options.quiet:
            verbose = False
        else:
            verbose = True

        #run tests and then exit
        if options.test:
            _test(verbose)
            sys.exit(0)

        if options.config:
            if __debug__:
                if LITEN_DEBUG_MODE == 2:
                    pdb.set_trace()
            process = ProcessConfig(filep=options.config)
            try:
                config = process.readConfig()
                print(config)
                path = config[0]
                size = config[1]
                pattern = config[2]
                print(("Using %s, path=%s, size=%s, pattern=%s" % \
                        (options.config, path,size, pattern)))
                start = Liten(spath = path,
                            fileSize = size,
                            pattern = pattern,
                            config = options.config)
                start.diskWalker()
                sys.exit(0)
            except configparser.Error as err:
                print(("Problem parsing config file: %s" % options.config))
                print(err)
                sys.exit(1)

        if len(arguments) > 0:
            for arg in arguments:
                if not os.path.isdir(arg):
                    print(("Search path does't exist or is not a directory: %s"\
                    % arg))
                    sys.exit(1)
            try:
                if options.delete:
                    actions_handler = ActionsAutomatic()
                else:
                    actions_handler = ActionsMixin()
                start = Liten(spath = arguments,
                            fileSize = options.size,
                            pattern = options.pattern,
                            reportPath=options.report,
                            verbose=verbose,
                            handler = actions_handler)
                start.diskWalker()
            #Here I catch bogus size input exceptions
            except UnboundLocalError as err:
                print(err)
                if LITEN_DEBUG_MODE == 1:
                    print(("Error: %s" % err))
                print(("Invalid Search Size Parameter: %s run --help for help"\
                % options.size))
                sys.exit(1)

        else:
            p.print_help()

def main():
    """run liten"""
    create = LitenController()
    create.run()

def _test(verbose=True):
    """run doctests"""

    if not os.path.isdir("tests/data"):
        sys.exit("Error: Running doctests requires 'tests/data' dir to be present")

    import doctest
    doctest.testmod(verbose=verbose)

if __name__ == "__main__":
    main()
