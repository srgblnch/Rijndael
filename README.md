Generalizing the Rijndael
=========================

This is just a probe of concept. You **MUST NOT** use this code in production projects.

The original schema of the [Rijndael](http://en.wikipedia.org/wiki/Advanced_Encryption_Standard) cryptosystem has one block size with 5 key lenghts. During the AES contest process this was restricted to 3 known key lenght sizes: 128, 192 and 256 bits (discating the options for 160 and 224). But the parameters flexibility of this schema allows even more posibilities.

The code has been made to academic cryptographic purposes and its cryptoanalysis hasn't start yet. It encrypts and decrypts, but it hasn't been demonstrated its properties like the original Rijndael has. The side-channel attacks neither wasn't studied yet, then they are not prevented in the current code stage.

Usage
-----

Cython compilation has been temporally removed until the development is completed. Then it will be when cython comes to the scene to introduce compilation to improve execution time and measure if there are differences between 32 and 64 architectures.

<!--To compile it uses the [cython](http://cython.org)'s *Distutils* module, the [setuptools](http://en.wikipedia.org/wiki/Setuptools) and the build from cython. Then just call:
```
$ python setup.py build
```

This will produce a '*GeneralizedRijndael.so*' in a new '*build*' directory if there wasn't any problem. As this is not a finished modules, the install process is not used, but this *so* file can be placed somewhere within the *$PYTHONPATH* or simlinked inside the test directory.

Even it is cythonized and can be compiled, by now the sources are pure python; then it can be executed as:

```
$ python GeneralizedRijndael/GeneralizedRijndael.py
```

And if it has been compiled and there is a '*GeneralizedRijndael.so*' available; then it can be executed as:

```
$ python grijndael.py
```

Check with the '--help' parameter to know more how to use it's parametering.-->

Testing
-------

Many of the modules inside have their own testing. They shall work simply by calling the file from python because they have a 'main' defined. Testing will require a refactoring to split what shall be a unit test and what's a simple check.

Extras
------

**TODO**