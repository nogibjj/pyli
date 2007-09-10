#!/usr/bin/env python
#09/09/07
#Liten 0.1.2
#A Deduplication Tool
#Author:  Noah Gift
#License: New BSD
#Copyright (c) 2007, Noah Gift
#
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
#Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#Neither the name of the Noah Gift, nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import os
import datetime
#import re                  #Need to implement
import sys
import string
import time
import optparse
#import shelve              #Need to implement
import md5
#import logging             #Need to implement logging

class FileType(object):                         #Need to implement
    """A class that holds file type attributes"""

    FileTypeMap = {".txt" : "Plain Text",
                    ".mp3" : "Music",
                    ".mp4" : "Music",
                    ".wav" : "Music",
                    ".pdf" : "Portable Document Format",
                    ".doc" : "Document"}

    def printMethod(self):
                                #Write duplicate line
        """Prints out current FileTypeMap Class Attributes."""
        print self.FileTypeMap

class FileRecord(FileType):     #Need to implement
    """A record class for holding information
    for a file on a file system. And for confirmed duplicates"""

    def __init__(self, name=None,
                    fullPath='__init__ method object in FileRecord',
                    modDate=None,
                    createDate=None,
                    dupNumber=None,
                    searchDate=None,
                    checksum=None,
                    bytes=None,
                    fileType=None,
                    fileExt=None):

        self.name = name
        self.fullPath = fullPath
        self.modDate = modDate
        self.createDate = createDate
        self.dupNumber = dupNumber
        self.searchDate = searchDate
        self.checksum = checksum
        self.bytes = bytes
        self.fileType = fileType
        self.fileExt = fileExt

    def test(self):
        print self.fullPath

    def info(self):
        return (self.name,
                self.fullPath,
                self.modDate,
                self.createDate,
                self.dupNumber,
                self.searchDate,
                self.checksum,
                self.bytes,
                self.fileType,
                self.fileExt)

class LitenBaseClass(FileRecord):
    """
    A base class for searching a file tree.

    Contains several methods for analyzing file objects.
    Main method is diskWalker, which walks filesystem and determines
    duplicates.

    >>> Liten = LitenBaseClass(spath='testData')
    >>> fakePath = 'testData/testDocOne.txt'
    >>> modDate = Liten.makeModDate(fakePath)
    >>> createDate = Liten.makeCreateDate(fakePath)
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
    >>> DupRecord = Liten.createDupRecord()
    >>> SearchDate = Liten.createSearchDate()
    >>> createExt = Liten.createExt(dupeFileOne)
    >>> createExt
    '.txt'

    """

    def __init__(self, spath=None, fileSizeMB=1, reportPath="LitenDuplicateReport.txt", verbose=True):
        FileRecord.__init__(self)
        self.spath = spath
        self.reportPath = reportPath
        self.fileSizeMB = fileSizeMB
        self.verbose = verbose
        self.checksum_cache_key = {}
        self.checksum_cache_value = {}
        self.confirmed_dup_key = {}
        self.confirmed_dup_value = {}
        self.byte_cache = {}
        self.master_key = {}
        self.master_value = {}

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
        try:
            fp = open(path)
            checksum = md5.new()
            for line in fp:
                checksum.update(line)
            fp.close()
            checksum = checksum.digest()
        except IOError:
            print "IO error for %s" % path
            checksum = None

        return checksum

    def createDupRecord(self):      #Need to implement
        pass

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


    def createRecord(self,path, file, key, value):  #Need to implement
        """
        Generically creates a file record
        """
        createDate = self.makeCreateDate(path)
        modDate = self.makeCreateDate(path)
        searchDate = self.createDate()
        fileType = None
        fileExt = createExt(file)
        value = {'fullPath': path,
                'modDate': modDate,
                'dupNumber': dupNumber,
                'searchDate': searchDate,
                'checksum': checksum,
                'bytes': bytes,
                'fileType': fileType,
                'fileExt': fileExt}
        return value

    def diskWalker(self):
        """Walks Directory Tree Looking at Every File, while performing a duplication match algorithm.

        Algorithm:
        This divides directory walk into doing either a more informed search if byte in key repository,
        or appending byte_size to list and moving to next file.  A md5 checksum is made of any file that has
        a byte size that has been found before.  The checksum is then used as the basis to determine duplicates.

        >> from liten import LitenBaseClass
        >>> Liten = LitenBaseClass(spath='testData')
        >>> Liten.diskWalker()
        Printing dups over 1 MB using md5 checksum: [SIZE] [ORIG] [DUP]
        <BLANKLINE>
        <BLANKLINE>
        LITEN REPORT:
        <BLANKLINE>
        Search Path:                  testData
        Total Files Searched:         3
        Duplicates Found:             0
        Wasted Space in Duplicates:   0  MB
        Report Generated at:          LitenDuplicateReport.txt
        Search Time:                  0  minutes
        <BLANKLINE>
        {}

        """
        spath = self.spath
        reportPath = self.reportPath
        fileSizeMB = self.fileSizeMB
        report = open(reportPath, 'w')
        main_path = os.walk(spath)
        byte_cache= self.byte_cache
        checksum_cache_key = self.checksum_cache_key
        checksum_cache_value = self.checksum_cache_value
        confirmed_dup_key = self.confirmed_dup_key
        confirmed_dup_value = self.confirmed_dup_value
        master_key = self.master_key
        master_value = self.master_value
        dupNumber=0
        byte_count=0
        record_count=0

        #times directory walk
        start = time.time()

        print "Printing dups over %s MB using md5 checksum: [SIZE] [ORIG] [DUP]" % fileSizeMB
        for root, dirs, files in main_path:
            for file in files:
                path = os.path.join(root,file)      #establishes full path
                if os.path.isfile(path):            #ignores symbolic links
                    byte_size = os.path.getsize(path)
                    record_count += 1                           #gets number of file examine
                    if byte_size >= fileSizeMB * 1048576:            #Note create hook for CLI later input size, patt match etc.
                        if byte_cache.has_key(byte_size):
                            checksum = self.createChecksum(path)

                            #checking to see if file has same checksum as checksum cache
                            if checksum_cache_key.has_key(checksum):
                                byte_count += byte_size                     #accumulates bytes of duplicates found
                                dupNumber += 1                              #accumulates a dupNumber record
                                #print byte_count/1048576, " MB's wasted"
                                #since we have a match, creating record with match partner and printing match original.
                                #grab original file path from checksum_cache dict
                                orig_path = checksum_cache_key[checksum]['fullPath']
                                orig_mod_date = checksum_cache_key[checksum]['modDate']
                                print byte_size/1048576, "MB ", "Orig: ", orig_path, "Dupe: ", path

                                #write out to report
                                report.write("Duplicate Version,     Path,       Size,       ModDate\n")
                                #Write original line
                                report.write("%s, %s, %s MB, %s\n" % ("Original", orig_path, byte_size/1048576, orig_mod_date))

                                #Gets Duplicates Modification Date
                                dupeModDate = self.makeCreateDate(path)

                                #Write duplicate line
                                report.write("%s, %s, %s MB, %s\n" % ("Duplicate", path, byte_size/1048576, dupeModDate))

                                #create original's record
                                confirmed_dup_key[orig_path] = checksum_cache_value          #Note this is a good spot for the dup rec count
                                #print "Original Duplicate: ", confirmed_dup_key[path]
                                #print confirmed_[checksum], byte_size/1048576, "MB ", self.makeCreateDate(path),  " ORIG"

                                #setrecord for duplicate match stored
                                confirmed_dup_value = {'fullPath': path,                    #duplicate code clean up later.
                                                        'modDate': modDate,
                                                        'dupNumber': dupNumber,
                                                        'searchDate': searchDate,
                                                        'checksum': checksum,
                                                        'bytes': byte_size,
                                                        'fileType': fileType,
                                                        'fileExt': fileExt}
                                confirmed_dup_key[path]=confirmed_dup_value
                                #print "duplicate file: ", path
                                #if self.verbose:
                                #    print checksum_cache[checksum], byte_size/1048576, "MB ", self.makeCreateDate(path),  " ORIG"
                                #    print path, byte_size/1048576, "MB ", self.makeCreateDate(path), " DUP"
                            else:
                                #get checksum of file that has a byte dupe match
                                checksum = self.createChecksum(path)
                                createDate = self.makeCreateDate(path)
                                modDate = self.makeCreateDate(path)                #Note I already grabbed this earlier
                                searchDate = self.createSearchDate()
                                fileExt = self.createExt(file)
                                fileType = None
                                checksum_cache_value = {'fullPath': path,                       #duplicate code clean up later.
                                                                'modDate': modDate,
                                                                'dupNumber': dupNumber,
                                                                'searchDate': searchDate,
                                                                'checksum': checksum,
                                                                'bytes': byte_size,
                                                                'fileType': fileType,
                                                                'fileExt': fileExt}

                                checksum_cache_key[checksum]=checksum_cache_value       #creating first checksum only dict.
                                #print "not a Dupe? ", path
                        else:
                            byte_cache[byte_size] = None
                            #pickle out file_system_record

        print "\n"
        print "LITEN REPORT: \n"
        print "Search Path:                 ", spath
        print "Total Files Searched:        ", record_count
        print "Duplicates Found:            ", len(confirmed_dup_key)
        print "Wasted Space in Duplicates:  ", byte_count/1048576, " MB"
        print "Report Generated at:         ", reportPath
        #get finish time
        end = time.time()
        timer = end - start
        timer = long(timer/60)
        print "Search Time:                 ", timer, " minutes\n"

        return  confirmed_dup_key   #Note returns a dictionary of all duplicate records

class GenerateDuplicationReport(object):
    """
    Not implemented yet.
    """
    pass

class LitenController(object):
    """
    Controller for DiskStat Command Line Tool.
    Handles optionparser parameters and setup.
    """

    def run(self):
        """Run method for Class"""
        p = optparse.OptionParser(description='A tool to examine your filesystem and find duplicates using md5 checksums.',
                                                prog='liten',
                                                version='liten 0.1a(alpha)',
                                                usage= '%prog [starting directory] [options]')
        p.add_option('--size', '-s', help='File Size in MB Threshold To Examine For Duplicates', default='1')
        options, arguments = p.parse_args()

        if len(arguments) == 1:
            spath = arguments[0]
            if options.size:
                fileSizeMB = int(options.size)
                start = LitenBaseClass(spath, fileSizeMB)
                value = start.diskWalker()
            elif options.doctest:
                _test()
            else:
                start = LitenBaseClass(spath)
                value = start.diskWalker()

            #for key in value:
            #    print key
        else:
            p.print_help()  #note if nothing is specified on the command line or if more than one parameter is specified, help is printed

class CreateVolumeMetadata(object):
    """
    Not implemented
    """
    pass

def _main():
    """
    Runs liten.
    """
    create = LitenController()
    create.run()
def _test():
    """
    Runs doctests
    """
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    """Looks for -v to run doctests else runs main application"""
    try:
        if sys.argv[1] == "-v":
           _test()
    except:
        _main()

