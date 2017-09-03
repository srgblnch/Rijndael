Using those polynomials
=======================

```python
>>> from gRijndael import Polynomials
>>> from random import randint
```

Polynomials over the binay field
--------------------------------

![equation](http://latex.codecogs.com/gif.latex?(%5Cmathbb{F}_{2^w])^l=%5Cmathbb{F}_{2^w}=%5Cmathbb{F}_{2^{w%5Ctimes l}=%5Cfrac{%5Cmathbb{F}_{2}[z]}{m(z)})

```python
>>> w = 8
>>> binRing = Polynomials.BinaryExtensionModulo(Polynomials.getBinaryExtensionRingModulo(w))
>>> binField = Polynomials.BinaryExtensionModulo(Polynomials.getBinaryExtensionFieldModulo(w))
```

Random elements:

```python
>>> element = binRing(randint(0, 2**w))
>>> element
z^7+z^6+z^4+z^3
>>> hex(element)
'0xd8'
>>> bin(element)
'0b11011000'
```

Operations

```python
>>> another = binRing(randint(0, 2**w))
>>> another
z^6+z+1
>>> element + another
z^7+z^4+z^3+z+1
>>> element * another
z^6+z^4+z^3+z^2+z+1
>>> element / another
z+1
```

Polynomials over a binary field extension
-----------------------------------------

![equation](http://latex.codecogs.com/gif.latex?%5Cmathbb{F}_{2^{w^l}}=%5Cfrac{%5Cmathbb{F}_{2^w}[x]}{l(x)})

```python
>>> l=4
>>> cx, ring, subfield = Polynomials.getPolynomialRingWithBinaryCoefficients(l, w)
>>> cx
(z+1)*x^3+x^2+x+(z) (mod x^4+1)
>>> hex(cx)
'0x3x^3+x^2+x+0x2'
>>> int(cx)
50397442
>>> hex(int(cx))
'0x3010102'
>>> dx = ~cx
>>> dx
(z^3+z+1)*x^3+(z^3+z^2+1)*x^2+(z^3+1)*x+(z^3+z^2+z) (mod x^4+1)
>>> hex(dx)
'0xBx^3+0xDx^2+0x9x+0xE'
```

Random elements:

```python
>>> ax = ring([randint(0, 2*w) for i in range(l)])
>>> ax
(z^2+z+1)*x^3+x^2+(z^2)*x+(z^3+z^2+1) (mod x^4+1)
>>> hex(ax)
'0x7x^3+x^2+0x4x+0xD'
```

Operations

```python
>>> ax + cx
(z^2)*x^3+(z^2+1)*x+(z^3+z^2+z+1) (mod x^4+1)
>>> ax * dx
(z^6+z^5+z^3)*x^3+(z^6+z^3+z)*x^2+(z^6+z^5+z^4+z^2+1)*x+(z^6+z^4+z^3) (mod x^4+1)
>>> ax / cx
(z^7+z^6+z^5+z^4+z^2) (mod x^4+1)
>>> ax * cx * dx
(z^2+z+1)*x^3+x^2+(z^2)*x+(z^3+z^2+1) (mod x^4+1)
```

