Date: 09/09/07
Author:  Noah Gift
Program: Liten
Version:  0.1.2 (Bleeding Edge Alpha Version of deduplicator software.  Just prints reports for now)

This command line tools detects duplicates by using a md5 checksum algorithm.
For the most, things should just work.  Duplicates and Originals get printed to stdout.
This is alpha status, so I would recommend being cautious at first with this tool, although
every effort has been made to ensure accuracy.

Please note, that currently this tool just "reports" duplicates and in fact generates a
handy CSV formatted report in your current directory.  Later versions will have sophisticated
deletion systems, cached query systems and more.  Stay tuned!

Note:  To run doctests run:  ./liten -v

To Do:

* Very weak unittests.  Will fix ASAP.
* Need deletion system
* Need cached query system.
* More command line options.
* Suggestions?



Questions?
noah.gift@gmail.com

