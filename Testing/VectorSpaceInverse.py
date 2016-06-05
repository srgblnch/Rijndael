import GeneralizedRijndael
fieldModulo = GeneralizedRijndael.Polynomials.getBinaryExtensionFieldModulo(8)
field = GeneralizedRijndael.Polynomials.BinaryExtensionModulo(fieldModulo,
                                                              variable='z')
vSpace = GeneralizedRijndael.Polynomials.VectorSpaceModulo('x^4+1', field)
# a = vSpace([3,3,3,3])
# b = vSpace([0,0,0,3])
# a.logLevel = 4
c = vSpace('(z+1)*x^3+x^2+x+(z)')
d = vSpace('(z^3+z+1)*x^3+(z^3+z^2+1)*x^2+(z^3+1)*x+(z^3+z^2+z)')
c.logLevel = 4
print("\nc*d = %s * %s = %s\n" % (c, d, c*d))
d_ = ~c
print("\nc^-1 = %s ^-1 = %s ?= %s = d\n" % (c, d_, d))
