#!/usr/bin/env python
#04/02/08
#Liten 0.1.4.3
#A Deduplication Tool
#Author:  Noah Gift
#License:  MIT License
#http://www.opensource.org/licenses/mit-license.php
#Copyright (c) 2007,2008 Noah Gift

"""
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

By default a report will be created in CWD, called LitenDuplicateReport.csv

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
A report named LitenDuplicateReport.csv will be created in your current working
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
"""

import os
import datetime
import re
import sys
import string
import time
import optparse
import hashlib
import pdb
import ConfigParser
from fnmatch import fnmatch

#Liten Debug Mode
#Environmental Variable Options:
#To enable print statement debugging set LITEN_DEBUG to 1
#To enable pdb break point debugging set LITEN_DEBUG to 2

if __debug__:
    LITEN_DEBUG_MODE = int(os.environ.get('LITEN_DEBUG', 0))
    MESSAGE = "LITEN DEBUG MODE ENABLED:"
    if LITEN_DEBUG_MODE == 1:
        print "%s Print Mode" % MESSAGE
    if LITEN_DEBUG_MODE == 2:
        print "%s pdb Mode" % MESSAGE
class ActionsMixin(object):
    """An Actions Mixin Class"""

    def remove(self, file, dryrun=False, interactive=False):
           """
           takes a path and deletes file/unlinks
           """
           #simulation mode for deletion
           if dryrun:
               print "Dry Run:  %s [NOT DELETED]" % file
               return None
           else:
               print "DELETING:  %s" % file
               try:
                   status = os.remove(file)
               except Exception, err:
                   print err
                   return status

           #interactive deletion mode
           if interactive:
               input = raw_input("Do you really want to delete %s [N]/Y" % file)
               if input == "Y":
                   print "DELETING:  %s" % file
                   try:
                       status = os.remove(file)
                   except Exception, err:
                       print err
                       return status
               elif input == "N":
                   print "Skipping:  %s" % file
                   return None
               else:
                   print "Skipping:  %s" % file
                   return None



class FileAttributes(object):

    def makeModDate(self,path):
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
                buffer = fp.read(8192)
                if not buffer:break
                checksum.update(buffer)
            fp.close()
            checksum = checksum.digest()
        except IOError:
            if self.verbose:
                print "IO error for %s" % path
            checksum = None
            if LITEN_DEBUG_MODE == 1:
                print 'IO error for %s' % path
        finally:
            if LITEN_DEBUG_MODE:
                print "Performing checksum on: %s" % path
        return checksum

    def createSearchDate(self):
        now = datetime.datetime.now()
        date = now.strftime("%Y%m%d")
        return date

    def createExt(self, file):
        """
        takes a file on a path and returns extension
        """
        (shortname, ext) = os.path.splitext(file)
        return ext

    def sizeType(self):
        """
        Calculates size based on input.

        Uses regex search of input to determine size type.
        """

        #optional pdb Debug Mode
        if LITEN_DEBUG_MODE == 2:
            pdb.set_trace()

        patterns = {'bytes': '1',
                    'KB': '1024',
                    'MB': '1048576',
                    'GB': '1073741824',
                    'TB': '1099511627776'}

        #Detects File Size Type, Strips off Characters
        #Converts value to bytes
        for key in patterns:
            value = patterns[key]
            try:
                #print self.fileSize
                if re.search(key, self.fileSize):
                    if LITEN_DEBUG_MODE:
                        print "Key: %s Filesize: %s " % (key, self.fileSize)
                        print "Value: %s " % value
                    byteValue = int(self.fileSize.strip(key)) * int(value)
                    #print "Converted byte value: %s " % byteValue
                else:
                    byteValue = int(self.fileSize.strip()) * int(1048576)
                    #print "Converted byte value: %s " % byteValue
            except Exception, err:
                if LITEN_DEBUG_MODE:
                    print "Problem evaluating:", self.fileSize, Exception, err
                else:
                    pass    #Note this gets caught using optparse which is cleaner
        return byteValue


class Liten(FileAttributes, ActionsMixin):
    """
    A base class for searching a file tree.

    Contains several methods for analyzing file objects.
    Main method is diskWalker, which walks filesystem and determines
    duplicates.

    You may modify the action that occurs when a duplicate is
    found my either creating an ActionsMixin method, or
    you can pass Liten a function that takes a file argument
    and process that file object.

    >>> Liten = Liten(spath='testData')
    >>> fakePath = 'testData/testDocOne.txt'
    >>> modDate = Liten.makeModDate(fakePath)
    >>> createDate = Liten.makeCreateDate(fakePath)
    >>> dupeFileOne = 'testData/testDocOne.txt'
    >>> checksumOne = Liten.createChecksum(dupeFileOne)
    >>> badChecksumAttempt = Liten.createChecksum('fileNotFound.txt')
    IO error for fileNotFound.txt
    >>> dupeFileTwo = 'testData/testDocTwo.txt'
    >>> checksumTwo = Liten.createChecksum(dupeFileTwo)
    >>> nonDupeFile = 'testData/testDocThree_wrong_match.txt'
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
                    delete = False,
                    action = False):

        self.spath = spath
        self.reportPath = reportPath
        self.config = config
        self.fileSize = fileSize
        self.pattern = pattern
        self.verbose = verbose
        self.checksum_cache_key = {}
        self.checksum_cache_value = {}
        self.confirmed_dup_key = {}
        self.confirmed_dup_value = {}
        self.byte_cache = {}
        self.matches = []
        self.delete = delete
        self.action = action

    def diskWalker(self):
        """Walks Directory Tree Looking at Every File, while performing a
        duplicate match algorithm.

        Algorithm:
        This divides directory walk into doing either a more informed search
        if byte in key repository, or appending byte_size to list and moving
        to next file.  A md5 checksum is made of any file that has a byte size
        that has been found before.  The checksum is then used as the basis to
        determine duplicates.

        (Note that test includes .svn directory)

        >> from liten import Liten
        >>> Liten = Liten(spath='testData', verbose=False)
        >>> Liten.diskWalker()
        {}

        """
        #optional pdb Debug Mode
        if __debug__:
            if LITEN_DEBUG_MODE == 2:
                pdb.set_trace()

        #Local Variables
        report = open(self.reportPath, 'w')
        main_path = os.walk(self.spath)
        if LITEN_DEBUG_MODE == 1:
            print "self.sizeType() %s" % self.sizeType()
        byteSizeThreshold = self.sizeType()
        dupNumber=0
        byte_count=0
        record_count=0

        #times directory walk
        start = time.time()

        if self.verbose:
            print "Printing dups over %s MB using md5 checksum: \
            [SIZE] [ORIG] [DUP] " % int(byteSizeThreshold/1048576)

        for root, dirs, files in main_path:
            for file in files:
                path = os.path.join(root,file)      #establishes full path
                if os.path.isfile(path):            #ignores symbolic links
                    self.byte_size = os.path.getsize(path)
                    #gets number of file examined
                    record_count += 1
                    #File Size, Pattern Filter Section
                    if self.byte_size >= byteSizeThreshold:
                        if fnmatch(path, self.pattern):		#default * match
                            if LITEN_DEBUG_MODE == 1:
                                print "Matches: %s" % path

                            if self.byte_size in self.byte_cache:
                                if LITEN_DEBUG_MODE == 1:
                                    print 'Doing checksum on %s' % path

                                #print "Doing checksum on %s" % path
                                checksum = self.createChecksum(path)

                                #checking to see if file has same checksum as checksum cache
                                if checksum in self.checksum_cache_key:
                                    #accumulates bytes of duplicates found
                                    byte_count += self.byte_size
                                    #accumulates a dupNumber record
                                    dupNumber += 1

                                    #print byte_count/1048576, " MB's wasted"
                                    #since we have a match, creating record with match partner
                                    #and printing match original.
                                    #grab original file path from checksum_cache dict

                                    orig_path = self.checksum_cache_key[checksum]['fullPath']
                                    orig_mod_date = self.checksum_cache_key[checksum]['modDate']
                                    if self.verbose:
                                        print self.byte_size/1048576, "MB ", "ORIG: ",\
                                        orig_path, "DUPE: ", path

                                    #write out to report
                                    report.write("Duplicate Version,     Path,      \
                                    Size,       ModDate\n")
                                    #Write original line
                                    report.write("%s, %s, %s MB, %s\n" % ("Original",\
                                    orig_path, self.byte_size/1048576, orig_mod_date))

                                    #Gets Duplicates Modification Date
                                    dupeModDate = self.makeCreateDate(path)

                                    #Write duplicate line
                                    report.write("%s, %s, %s MB, %s\n" % ("Duplicate",\
                                    path, self.byte_size/1048576, dupeModDate))

                                    #Runtime Decision
                                    if self.action:
                                        self.action(path)
                                    else:
                                        if self.delete:
                                            self.remove(path)

                                    #Note this is a good spot for the dup rec count
                                    self.confirmed_dup_key[orig_path] = self.checksum_cache_value

                                    #setrecord for duplicate match stored
                                    #duplicate code clean up later.
                                    confirmed_dup_value = {'fullPath': path,
                                                            'modDate': modDate,
                                                            'dupNumber': dupNumber,
                                                            'searchDate': searchDate,
                                                            'checksum': checksum,
                                                            'bytes': self.byte_size,
                                                            'fileType': fileType,
                                                            'fileExt': fileExt}
                                    self.confirmed_dup_key[path]=confirmed_dup_value

                                else:
                                    #get checksum of file that has a byte dupe match
                                    checksum = self.createChecksum(path)
                                    createDate = self.makeCreateDate(path)
                                    modDate = self.makeCreateDate(path)
                                    #Note I already grabbed this earlier
                                    searchDate = self.createSearchDate()
                                    fileExt = self.createExt(file)
                                    fileType = None
                                    #duplicate code clean up later.
                                    self.checksum_cache_value = {'fullPath': path,
                                                                    'modDate': modDate,
                                                                    'dupNumber': dupNumber,
                                                                    'searchDate': searchDate,
                                                                    'checksum': checksum,
                                                                    'bytes': self.byte_size,
                                                                    'fileType': fileType,
                                                                    'fileExt': fileExt}

                                    #creating first checksum only dict.
                                    self.checksum_cache_key[checksum]=self.checksum_cache_value
                                    #print "not a Dupe? ", path
                            else:
                                self.byte_cache[self.byte_size] = None
                                #pickle out file_system_record

        if self.verbose:
            print "\n"
            print "LITEN REPORT: \n"
            print "Search Path:                 ", self.spath
            print "Filtered For Pattern Match:  ", self.pattern
            if self.config:
                print"Used config file:            ",self.config
            print "Total Files Searched:        ", record_count
            #print "Duplicates Found:            ", #incorrect numberlen(self.confirmed_dup_key)
            print "Wasted Space in Duplicates:  ", byte_count/1048576, " MB"
            print "Report Generated at:         ", self.reportPath
            #get finish time
            end = time.time()
            timer = end - start
            timer = long(timer/60)
            print "Search Time:                 ", timer, " minutes\n"

        return  self.confirmed_dup_key   #Note returns a dictionary of all duplicate records

class ProcessConfig(object):
    """
    Reads in optional configuration file that replaces command line options
    """
    def __init__(self, file="config.ini"):
        self.file = file

    def readConfig(self):
        """reads and processes config file and returns results"""

        Config = ConfigParser.ConfigParser()
        Config.read(self.file)
        sections = Config.sections()
        for parameter in sections:
            #uncomment line below to see how this config file is parsed
            #print Config.items(parameter)
            try:
                path = Config.items(parameter)[0][1]
                if LITEN_DEBUG_MODE == 1:
                    print "Config file path: %s" % path
            except:
                path = None
            try:
                pattern = Config.items(parameter)[1][1]
                if LITEN_DEBUG_MODE == 1:
                    print "Config file pattern: %s" % pattern
            except:
                pattern = None
            try:
                size = Config.items(parameter)[2][1]
                if LITEN_DEBUG_MODE == 1:
                    print "Config file size: %s" % size
            except:
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

        descriptionMessage = """
        A command line tool for detecting duplicates using md5 checksums.
        """

        p = optparse.OptionParser(description=descriptionMessage,
                                    prog='liten',
                                    version='liten 0.1.4',
                                    usage= '%prog [starting directory] [options]')
        p.add_option('--config', '-c',
                    help='Path to read in config file')
        p.add_option('--size', '-s',
                    help='File Size Example:  10bytes, 10KB, 10MB,10GB,10TB, or \
                    plain number defaults to MB (1 = 1MB)',
                    default='1MB')
        p.add_option('--pattern', '-p',
                    help='Pattern Match Examples: *.txt, *.iso, music[0-5].mp3\
                    plain number defaults to * or match all.  \
                    Uses UNIX standard wildcard syntax.',
                    default='*')
        p.add_option('--quiet', '-q', action="store_true",
                    help='Suppresses all STDOUT.',default=False)
        p.add_option('--delete', '-d', action="store_true",
                    help='DELETES all duplicate matches permanently!',default=False)
        p.add_option('--report', '-r',
                    help='Path to store duplicate report. Default CWD',
                    default='LitenDuplicateReport.csv')
        p.add_option('--test', '-t', action="store_true",help='Runs doctest.')

        options, arguments = p.parse_args()

        #run tests and then exit
        if options.test:
            _test()
            sys.exit(0)
        if options.config:
            if __debug__:
                if LITEN_DEBUG_MODE == 2:
                    pdb.set_trace()
            process = ProcessConfig(file=options.config)
            try:
                config = process.readConfig()
                print config
                path = config[0]
                size = config[1]
                pattern = config[2]
                print "Using %s, path=%s, size=%s, pattern=%s" % \
                        (options.config, path,size, pattern)
                start = Liten(spath = path,
                            fileSize = size,
                            pattern = pattern,
                            config = options.config)
                start.diskWalker()
                sys.exit(0)
            except Exception, err:
                print "Problem parsing config file: %s" % options.config
                print err
                sys.exit(1)

        if options.quiet:
            verbose = False
        else:
            verbose = True
        if len(arguments) == 1:
            try:
                start = Liten(spath = arguments[0],
                            fileSize = options.size,
                            pattern = options.pattern,
                            reportPath=options.report,
                            verbose=verbose,
                            delete = options.delete)
                start.diskWalker()
            #Here I catch bogus size input exceptions
            except UnboundLocalError, err:
                print err
                if LITEN_DEBUG_MODE == 1:
                    print "Error: %s" % err
                print "Invalid Search Size Parameter: %s run --help for help"\
                % options.size
                sys.exit(1)

        else:
            p.print_help()

def main():
    """Runs liten."""
    create = LitenController()
    create.run()

def _test():
    """Runs doctests."""
    import doctest
    doctest.testmod(verbose=True)

if __name__ == "__main__":
    main()
