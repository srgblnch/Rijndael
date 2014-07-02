Generalizing the Rijndael
=========================

This is just a probe of concept. You **MUST NOT** use this code in production projects.

This has been developed to study the possibility to generalize the [Rijndael](http://en.wikipedia.org/wiki/Advanced_Encryption_Standard) schema, originally for any multiple of 32 bits between 128 and 256 for both block and key sizes, but the AES standard cuts it to 1 block size of 128 and 3 key sizes of 128, 192 and 256.

The code has been made to cryptographic purposes and its cryptoanalysis hasn't start yet. It encrypts and decrypts, but it hasn't been demonstrated its properties like the original Rijndael has. The side-channel attacks neither wasn't studied yet, then they are not prevented in the current code stage.

Usage
-----

To compile the [cython](http://cython.org) module, just call:
```
$ python setup.py build
```

This will produce a '*GeneralizedRijndael.so*' in a new '*build*' directory if there wasn't any problem. As this is not finished, for testing purposes, you can manually symlink this '*GeneralizedRijndael.so*' file to the test directory, and do the same linking for the '*sboxes.py*' and '*version.py*' in the GeneralizedRijndael directory.

Testing
-------

At this point you should be able to call, from in side the test directory:
```
$ python aesTest.py
```
To do a simple, but complete, test of the 3 key sizes of the standardized AES (with a debug output to be able to check the information provided in the standard itself).

*keyExpansionTest* is a python script used to generate three random numbers (128, 192 and 256 bits) and do with them the key expansion operation for each size,

The *unitTest* script does one single unit test with pre-established sets of data for each of the 4 Rijndael operations.

*rijndael32Test* is an script to check a reduced version of the Rijndael over 32 bit data blocks. This size can be reached by two different parameter combinations: 2 rows, 2 columns and 8 bit wordsize; or 4 rows, 4 columns and 2 bit wordsize. The key sizes are also reduced (remember this module has academic purposes) to be 32, 48, 64 and 128 bits (with the two parameter combination ways to reach them). And finally there is a loop of a hundred random cypher-decypher pairs of 32 bit blocks with 128 bit keys (also with both ways).

Finally the most general test file is *rijndaelTest* where the test can be fine tuned using command line parameters. For example to set the AES standard sizes:
```
    $ python rijndaelTest.py --sizes=10,4,4,8
      state matrix 4*4, wordsize 8 bits, 10 rounds (key with 4 columns)
    $ python rijndaelTest.py --sizes=12,4,4,8,8
      state matrix 4*4, wordsize 8 bits, 12 rounds (key with 6 columns)
    $ python rijndaelTest.py --sizes=14,4,4,8,8
      state matrix 4*4, wordsize 8 bits, 14 rounds (key with 8 columns)
```
Or other sizes can be also set like for example a 48 bit block and 80 bit keys:
```
    $ python rijndaelTest.py --sizes=40,2,3,8,5
      state matrix 2*3, wordsize 8 bits, 40 rounds (key with 5 columns)
```
Note: There are unsupported (yet) key sizes like odd word sizes or bigger than 8. The number of rows can only be in 2,3,4.

Extras
------

There is an extra module (link it like the other stuff) called 'armor' that has been created to check the viability of this generalization in a ticketing system. The example suppose that 3 fields (natural numbers of 17, 16 and 8 bits respectively) have to be codified in a single alphanumeric code of 10 characters.

As a sample, given three random number in the ranges 103030,10660,49 and a random key:
```
    $ python testCode.py -g 103030,10660,49 -k 0x789509a827e22ef3538cd4e19dc4f41c
        For Ofert: 103030       Bonus:10660     with attrs:49 (crc 0x5)
        The code is 2GUICHDEJM (base36)(len 10)
```
And the inverse operation:
```
    $ python testCode.py -v 2GUICHDEJM -k 0x789509a827e22ef3538cd4e19dc4f41c
        Valid: ofert: 103030, bonus: 10660, attributes: 49, crc: 0x5
```
It can be also set up a loop of N tries using random data in the ranges:
```
    $ python testCode.py -l N
```
