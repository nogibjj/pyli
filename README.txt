Liten - Command Line Tool and Library to Eliminate Duplicates
###############################################################

Usage Example:

    ```
    pyli git:(master) ✗ python liten.py ~/Desktop    
    Printing dups over 1 MB using md5 checksum:             [SIZE] [ORIG] [DUP] 
    ```




Author: Noah Gift
License: MIT

Contributors:
* Rick Copeland
* Titus Brown
* Shannon Behrens
* Anatoly Techtonik


Documentation:
See docs/index.txt for details

Tests and lintint:
make all
* Run tests/test_create_file.py to create some files in temporary
  directory and then delete those files using liten::
    python liten.py --delete /tmp
