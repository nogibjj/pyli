#!/usr/bin/env python
#unittests for liten
import unittest
import doctest
from doctest import DocTestSuite

from os.path import abspath,dirname,join
from liten import Liten

class TestLitenBaseClass(unittest.TestCase):
    """Tests for LitenBaseClass Class."""

    def setUp(self):
        # absolute path to ./data dir
        self.testData = join(dirname(abspath(__file__)), "data")

        self.fakePath = join(self.testData, 'testDocOne.txt')
        self.dupeFileOne = join(self.testData, 'testDocOne.txt')
        self.dupeFileTwo = join(self.testData, 'testDocTwo.txt')
        self.nonDupeFile = join(self.testData, 'testDocThree_wrong_match.txt')

        #Tests byte size calculations and conversions
        self.byteFileSize = '1bytes' #1 bytes
        self.KBFileSize = '1KB' #1024 bytes
        self.MBFileSize = '1MB' #1048576 bytes
        self.GBFileSize = '1GB' #1073741824 bytes
        self.TBFileSize = '1TB' #1099511627776 bytes
        self.NoQualifier = '1' #No Qualifier defaults to MB/ 1048576 bytes
        self.Bogus = '9foo' #Bogus data


    def testModDate(self):
        """Test modDate method."""
        liten = Liten(spath='testData')
        modDate = liten.makeModDate(self.fakePath)

    def testCreateDate(self):
        """Test createDate method."""
        liten = Liten(spath='testData')
        createDate = liten.makeCreateDate(self.fakePath)

    def badChecksumDetection(self):
        """Bad Checksum Detection Should Raise Exception."""
        liten = Liten(spath='testData')
        badChecksumAttempt = liten.createChecksum('fileNotFound.txt')


    def testDupeFileDetection(self):
        """Test checksum of duplicate files"""
        liten = Liten(spath='testData')
        checksumOne = liten.createChecksum(self.dupeFileOne)
        checksumTwo = liten.createChecksum(self.dupeFileTwo)
        self.assertEqual(checksumOne, checksumTwo)

    def testDupeFileDetectionError(self):
        """Test checksum of Non-duplicate files"""
        liten = Liten(spath='testData')
        checksumOne = liten.createChecksum(self.dupeFileOne)
        checksumThree= liten.createChecksum(self.nonDupeFile)
        self.assertNotEqual(checksumOne, checksumThree)

    def testCreateExt(self):
        """Test Create Extension Method."""
        liten = Liten(spath='testData')
        createExt = liten.createExt(self.dupeFileOne)
        self.assertEqual(createExt, ".txt")

    def testByteconvertSize(self):
        """Tests ByteSize Calculations based on Input."""
        liten = Liten(spath='testData', fileSize=self.byteFileSize)
        byteconvertSize = liten.convertSize(liten.fileSize)
        self.assertEqual(byteconvertSize, 1)

    def testKByteconvertSize(self):
        """Tests KBSize Calculations based on Input."""
        self.assertEqual(Liten().convertSize(self.KBFileSize), 1024)

    def testMBByteconvertSize(self):
        """Tests MBSize Calculations based on Input."""
        self.assertEqual(Liten().convertSize(self.MBFileSize), 1048576)

    def testGBconvertSize(self):
        """Tests GBSize Calculations based on Input."""
        self.assertEqual(Liten().convertSize(self.GBFileSize), 1073741824)

    def testTBconvertSize(self):
        """Tests TBSize Calculations based on Input."""
        self.assertEqual(Liten().convertSize(self.TBFileSize), 1099511627776)

    def testNoQualifier(self):
        """Tests NoSize Calculations based on Input.

        Should convert No Qualifiers to MB
        """
        liten = Liten(spath='testData', fileSize=self.NoQualifier)
        self.assertEqual(liten.convertSize(liten.fileSize), 1048576)

    def testBogus(self):
        """Tests Bogus Size Input.

        Should raise exception ValueError or fail
        """
        liten = Liten(spath='testData', fileSize=self.Bogus)
        self.assertRaises(ValueError, liten.convertSize, liten.fileSize)


if __name__ == '__main__':
    # add liten package path to PYTHONPATH
    import sys
    sys.path.append(dirname(dirname(abspath(__file__))))

    from liten import Liten, LitenController

    unittest.main()

