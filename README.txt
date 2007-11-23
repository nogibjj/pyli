Date: 11/23/07
Author:  Noah Gift
Program: Liten
Version:  0.1.3 (Just Prints Report)

This command line tools detects duplicates by using a md5 checksum algorithm.
For the most, things should just work.  Duplicates and Originals get printed to stdout.
This is alpha status, so I would recommend being cautious at first with this tool, although
every effort has been made to ensure accuracy.

Please note, that currently this tool just "reports" duplicates and in fact generates a
handy CSV formatted report in your current directory.  Later versions will have sophisticated
deletion systems, cached query systems and more.  Stay tuned!

Note:  To run doctests run:  ./liten -v, or test_liten.py for unittests

CHANGE LOG:

Added with 0.1.3:

* Got rid of cruft.

Added with 0.1.2:

* Added -q or quiet option which supresses stdout.
* Added more flexibility with -s or --size option:
Now able to use bytes, KB, MB, GB, TB or just a number:

Example Size Option Usage:

liten.py -s 1 /mnt/raid         is equal to liten.py -s 1MB /mnt/raid
liten.py -s 1bytes /mnt/raid
liten.py -s 1KB /mnt/raid
liten.py -s 1MB /mnt/raid
liten.py -s 1GB /mnt/raid
liten.py -s 1TB /mnt/raid

The duplicate printing only reflects values about MB for now.  Will fix in 0.1.3

* Extensive doctests
* Extensive unittests


FUTURE PLANS:
    
* Need deletion system
* Need cached query system.
* More command line options.
* Suggestions?

Questions?
noah.gift@gmail.com

