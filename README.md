Generalizing the Rijndael
=========================

**Development Status :: 1 - Planning**

This is just a probe of concept. You **MUST NOT** use this code in production projects.

The original schema of the [Rijndael](http://en.wikipedia.org/wiki/Advanced_Encryption_Standard) cryptosystem has one block size with 5 key lenghts. During the AES contest process this was restricted to 3 known key lenght sizes: 128, 192 and 256 bits (discating the options for 160 and 224). But the parameters flexibility of this schema allows even more posibilities.

The code has been made to academic cryptographic purposes and its cryptoanalysis hasn't start yet. It encrypts and decrypts, but it hasn't been demonstrated its properties like the original Rijndael has. The side-channel attacks neither wasn't studied yet, then they are not prevented in the current code stage.

Install
-------

To install this code as a python module is needed to have **setuptools** 
available. Then only the following commands are needed:

```
$ python setup.py build
$ python setup.py install
```

Remember to use *--prefix* on the install if you like to do the installation
on an specific directory.

This module has been made to be compiled to improve execution time, but 
specially to measure differences between 32 and 64 bit architectures setting
up different parameter combinations. Now it is under a hard development 
process but, as soon as it has completed all the mathematical elements, 
*cython* will come to the scene to have architecture dependant binaries to 
check difference between them.

Testing
-------

For (something like) unit testing, no installation is required. Many of the 
modules in the directory *GeneralizedRijndael* have their own testing to be 
called from the command line using a python promt. Testing will require a 
refactoring itself to split what shall be a unit test and what's a simple 
check.

Extras
------

```python
>>> import GeneralizedRijndael
>>> GeneralizedRijndael.version()
'0.2.0-0'
```

The main constructor available in this module is 
*GeneralizedRijndael.GeneralizedRijndael*. A little help in the docstring 
shall be made soon, but there can be listed the arguments that this constructor
can have. With:

```python
>>> from random import randint
>>> k = randint(0,2**128-1)
>>> rijndael128 = GeneralizedRijndael.GeneralizedRijndael(k)
```

The *rijndael* object is configured, with a **non secure** random key, like a
standard *rijndael 128*: a block size of 128 (with a state matrix of 4x4 cells
with 8 bits on each) and a key with the same size and 10 rounds process.

The test vectors from the Rijndael's standard can be used. But also something 
more, on the fly like:

```python
>>> m = randint(0,2**128-1); c = rijndael128.cipher(m); c
23544119155075312493179623650411912571L
>>> m == rijndael128.decipher(c)
True
```
To have different Rijndael's standard sizes, the constructor shall be used:

```python
>>> k = randint(0,2**192-1)
>>> rijndael192 = GeneralizedRijndael.GeneralizedRijndael(k,nRounds=12,nKeyWords=6)
>>> k = randint(0,2**256-1)
>>> rijndael256 = GeneralizedRijndael.GeneralizedRijndael(k,nRounds=14,nKeyWords=8)
```

Many other sizes can be used. But with wordsizes different the *8*, the 
parameter *sboxCalc* shall be set to True. Otherwise you'll have an exception
because there aren't sboxes for any other size than 8.
