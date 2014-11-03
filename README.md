Generalizing the Rijndael
=========================

This is just a probe of concept. You **MUST NOT** use this code in production projects.

The original schema of the [Rijndael](http://en.wikipedia.org/wiki/Advanced_Encryption_Standard) cryptosystem has one block size with 5 key lenghts. During the AES contest process this was restricted to 3 known key lenght sizes: 128, 192 and 256 bits (discating the options for 160 and 224). But the parameters flexibility of this schema allows even more posibilities.

The code has been made to academic cryptographic purposes and its cryptoanalysis hasn't start yet. It encrypts and decrypts, but it hasn't been demonstrated its properties like the original Rijndael has. The side-channel attacks neither wasn't studied yet, then they are not prevented in the current code stage.

Usage
-----

To compile the [cython](http://cython.org) module, just call:
```
$ python setup.py build
```

This will produce a '*GeneralizedRijndael.so*' in a new '*build*' directory if there wasn't any problem. As this is not a finished modules, the install process is not made, but this *so* file can be placed somewhere within the *$PYTHONPATH* or simlinked inside the test directory. Two py files will be needed also in same place, the '*sboxes.py*' and '*version.py*', from the GeneralizedRijndael directory.

Testing
-------

**TODO**

Extras
------

**TODO**