#!/usr/bin/env python
#unittests for liten
import unittest

from liten import LitenBaseClass, LitenController, FileType, FileRecord

class LitenTest(unittest.TestCase):
    """
    Note, I am just testing very basic things right now.
    Will fix ASAP.
    """

    def testLitenBaseClass(self):
        self.assertRaises(TypeError, LitenBaseClass())
    def testLitenController(self):
        self.assertRaises(TypeError, LitenController())
    def testFileType(self):
        self.assertRaises(TypeError, FileType())
    def testFileRecord(self):
        self.assertRaises(TypeError, FileRecord())

if __name__ == '__main__':
    unittest.main()

