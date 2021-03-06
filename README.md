Generalizing the Rijndael
=========================

Summary
-------

![license GPLv3+](https://img.shields.io/badge/license-GPLv3+-green.svg) ![about](https://img.shields.io/badge/Subject-cryptography-orange.svg?style=social) ![3 - Alpha](https://img.shields.io/badge/Development_Status-3_--_alpha-orange.svg) ![Codeship badge](https://codeship.com/projects/43e4bce0-72ae-0134-b36e-76d603c7c101/status?branch=master)



You can consider this as a *toy project*, or a *probe of concept*. You **MUST NOT** use this code in production projects. This development is part of a research project and there are still many checks to be made.

The original schema of the [Rijndael](http://en.wikipedia.org/wiki/Advanced_Encryption_Standard) cryptosystem has one block size with 5 key lengths. During the AES contest process this was restricted to 3 known key length sizes: 128, 192 and 256 bits (discarding the options for 160 and 224). But the parameters flexibility of this schema allows even more possibilities.

The code has been made to **academic cryptographic purposes** and its cryptoanalysis hasn't start yet. It encrypts and decrypts, but it hasn't been demonstrated its properties like the original Rijndael has. The side-channel attacks neither hasn't been studied yet, then they are not prevented in the current code stage.

Install
-------

To install this code as a python module is needed to have **setuptools** available. Then only the following commands are needed:

```
$ python setup.py build
$ python setup.py install
```

Remember to use *--prefix* on the install if you like to do the installation on an specific directory. Remember that, depending on where you like to do the installation, your user may not have write permission and perhaps is needed to launch the install call with sudo (in case your user is a sudoer).

This module is pure python right now, it has been thought to compile it to improve execution time, but specially to measure differences between 32 and 64 bit architectures setting up different parameter combinations. Now it is under a hard development process but, as soon as it has completed all the mathematical elements, *cython* will come to the scene to have architecture dependent binaries to check difference between them.

Testing
-------

For (something like) unit testing, no installation is required. Many of the modules in the directory *gRijndael* have their own testing to be called from the command line using a python prompt. Testing will require a *refactoring* itself to split what shall be a unit test and what's a simple 
check.

Extras
------

```python
>>> import gRijndael
>>> gRijndael.version()
'0.4.0-0'
```

The main constructor available in this module is *gRijndael.gRijndael*. A little help in the *docstring* shall be made soon, but there can be listed the arguments that this constructor can have. With:

```python
>>> from random import randint
>>> k = randint(0, 2**128-1)
>>> rijndael128 = gRijndael.gRijndael(k)
>>> rijndael128.blockSize, rijndael128.keySize, rijndael128.nRounds
(128, 128, 10)
```

The *rijndael* object is configured, with a **non secure** random key, like a standard *rijndael 128*: a block size of 128 (with a state matrix of 4x4 cells with 8 bits on each) and a key with the same size and 10 rounds process.

Information about the build object can be read using some python properties (like the block size, key size and number of rounds has been shown in the previous sample code):

Columns, rows and wordsize:
```python
>>> rijndael128.nColumns, rijndael128.nRows, rijndael128.wordSize
(4, 4, 8)
```

Number of columns for the key:

```python
>>> rijndael128.nKeyColumns
4
```

Or deeper details about the *SBOX*:

```python
rijndael128.sbox.Field, rijndael128.sbox.Ring, rijndael128.sbox.Mu, rijndael128.sbox.Nu
('z^8+z^4+z^3+z+1', 'z^8+1', z^4+z^3+z^2+z+1, z^6+z^5+z+1)
```

Those are polynomials from the original Rijndael for this parameter combintaion.

And details about the *MixColumns* maths:

```python
rijndael128.mixColumns.PolynomialRingModulo, rijndael128.mixColumns.SubfieldModulo, rijndael128.mixColumns.Cx, rijndael128.mixColumns.Dx
('x^4+1', 'z^8+z^4+z^3+z+1', '0x3x^3+x^2+x+0x2', '0xBx^3+0xDx^2+0x9x+0xE')
```

The test vectors from the Rijndael's standard can be used. But also something more, on the fly like:

```python
>>> m = randint(0, 2**128-1); c = rijndael128.cipher(m); c
23544119155075312493179623650411912571L
>>> m == rijndael128.decipher(c)
True
```
To have different Rijndael's standard sizes, the constructor shall be used:

```python
>>> k = randint(0, 2**192-1)
>>> rijndael192 = gRijndael.gRijndael(k, nKeyColumns=6)
>>> rijndael192.blockSize, rijndael192.keySize, rijndael192.nRounds
 (128, 192, 12)
>>> k = randint(0,2**256-1)
>>> rijndael256 = gRijndael.gRijndael(k, nKeyColumns=8)
>>> rijndael256.blockSize, rijndael256.keySize, rijndael256.nRounds
 (128, 256, 14)
```

And the non-standardised but present in the original proposal with *160* and 
*224* bits on the key size:

```python
>>> k = randint(0, 2**160-1)
>>> rijndael160 = gRijndael.gRijndael(k, nKeyColumns=5)
>>> rijndael160.blockSize, rijndael160.keySize, rijndael160.nRounds
 (128, 160, 11)
>>> k = randint(0, 2**224-1)
>>> rijndael224 = gRijndael.gRijndael(k, nKeyColumns=7)
>>> rijndael224.blockSize, rijndael224.keySize, rijndael224.nRounds
 (128, 224, 13)
```

Many other sizes can be used. But with *wordsizes* different the *8*, the parameter *sboxCalc* shall be set to True. Otherwise you'll have an exception because there aren't *sboxes* for any other size than 8.

Continuing with examples, it can be used to have block of *256* bits together with a key of the same size:

```python
>>> k = randint(0, 2**256-1)
>>> rijndael256k256 = gRijndael.gRijndael(k, nKeyColumns=8, nColumns=8)
>>> rijndael256k256.blockSize, rijndael256k256.keySize, rijndael256k256.nRounds
 (256, 256, 14)
>>> m = randint(0, 2**256-1); c = rijndael256k256.cipher(m); m == rijndael256k256.decipher(c)
```

Or doubling the current limits of the standard with blocks of *256* bits and key of 512.

```python
>>> k = randint(0, 2**512-1)
>>> rijndael256k512 = gRijndael.gRijndael(k, nKeyColumns=16, nColumns=8)
>>> rijndael256k512.blockSize, rijndael256k512.keySize, rijndael256k512.nRounds
 (256, 512, 22)
>>> m = randint(0, 2**256-1); c = rijndael256k512.cipher(m); m == rijndael256k512.decipher(c)
```

Or reduce the block size having a bigger key size than in the standard:

```python
>>> k = randint(0, 2**512-1)
>>> rijndael32k512 = gRijndael.gRijndael(k, nKeyColumns=32, nColumns=2, nRows=2)
>>> rijndael32k512.blockSize, rijndael32k512.keySize, rijndael32k512.nRounds
 (32, 512, 38)
>>> m = randint(0, 2**32-1); c = rijndael32k512.cipher(m); m == rijndael32k512.decipher(c)
```

But here is where this generalisation takes its sense. To have 512 bits in the key, they can use *4* rows with the *16* like in the example (it uses 8 bits words). But those *512* bits can be achieved with *8* rows and *8* columns. The for all the sizes because, even the ones in the standard can be set up but with different parameter combinations.

This code is still under development, not only for its cryptoanalysis, but also because not all the parameter combination are already available.
