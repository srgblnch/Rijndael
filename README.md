Generalizing the Rijndael
=========================

This is just a probe of concept. You **MUST NOT** use this code in production projects.

The original schema of the [Rijndael](http://en.wikipedia.org/wiki/Advanced_Encryption_Standard) cryptosystem has one block size with 5 key lenghts. During the AES contest process this was restricted to 3 known key lenght sizes: 128, 192 and 256 bits (discating the options for 160 and 224). But the parameters flexibility of this schema allows even more posibilities.

The code has been made to academic cryptographic purposes and its cryptoanalysis hasn't start yet. It encrypts and decrypts, but it hasn't been demonstrated its properties like the original Rijndael has. The side-channel attacks neither wasn't studied yet, then they are not prevented in the current code stage.

Usage
-----

**TODO**

Testing
-------

**TODO**

Extras
------

**TODO**