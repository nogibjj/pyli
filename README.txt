A deduplication command line tool and library.  A relatively efficient
algorithm based on filtering like sized bytes, and then performing a full
md5 checksum, is used to determine duplicate files/file objects.

Example CLI Usage:

liten.py -s 1 /mnt/raid         is equal to liten.py -s 1MB /mnt/raid
liten.py -s 1bytes /mnt/raid
liten.py -s 1KB /mnt/raid
liten.py -s 1MB /mnt/raid
liten.py -s 1GB /mnt/raid
liten.py -s 1TB /mnt/raid

Example Library Usage:

Currently Liten is optimized for CLI use, but more library friendly changes
are coming.

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

Tests:

 * Run Doctests:  ./liten -t or --test
 * Run test_liten.py

Display Options:

STDOUT:

stdout will show you duplicate file paths and sizes such as:

Printing dups over 1 MB using md5 checksum: [SIZE] [ORIG] [DUP]
7 MB  Orig:  /Users/ngift/Downloads/bzr-0-2.17.tar
Dupe:  /Users/ngift/Downloads/bzr-0-4.17.tar

REPORT:

A report named LitenDuplicateReport.txt will be created in your current working
directory.

Duplicate Version,     Path,       Size,       ModDate
Original, /Users/ngift/Downloads/bzr-0-2.17.tar, 7 MB, 07/10/2007 01:43:12 AM
Duplicate, /Users/ngift/Downloads/bzr-0-3.17.tar, 7 MB, 07/10/2007 01:43:27 AM


DEBUG MODE ENVIRONMENTAL VARIABLES:

To enable print statement debugging set LITEN_DEBUG to 1
To enable pdb break point debugging set LITEN_DEBUG to 2
LITEN_DEBUG_MODE = int(os.environ.get('LITEN_DEBUG', 0))
Note:  When DEBUG MODE is enabled, a message will appear to standard out

QUESTIONS:  noah.gift@gmail.com
