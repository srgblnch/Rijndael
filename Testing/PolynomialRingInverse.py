import traceback
import GeneralizedRijndael
fieldModulo = GeneralizedRijndael.Polynomials.getBinaryExtensionFieldModulo(8)
field = GeneralizedRijndael.Polynomials.BinaryExtensionModulo(fieldModulo,
                                                              variable='z')
ring = GeneralizedRijndael.Polynomials.PolynomialRingModulo('x^4+1', field)

c = ring('(z+1)*x^3+x^2+x+(z)')
print("c = %s = %s" % (c, hex(c)))
d = ring('(z^3+z+1)*x^3+(z^3+z^2+1)*x^2+(z^3+1)*x+(z^3+z^2+z)')
print("d = %s = %s" % (d, hex(d)))
try:
    d_ = ~c
    print("\nc^-1 = %s ^-1 = %s ?= %s = d\n" % (c, d_, d))
except Exception as e:
    print("Exception: %s" % e)
    traceback.print_exc()

print c.hammingWeight
print c.hammingWeightPerCoefficient
print d.hammingWeight
print d.hammingWeightPerCoefficient