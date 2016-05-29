import GeneralizedRijndael
field = GeneralizedRijndael.Polynomials.BinaryExtensionModulo(GeneralizedRijndael.Polynomials.getBinaryExtensionFieldModulo(8), variable='z')
vSpace = GeneralizedRijndael.Polynomials.VectorSpaceModulo('x^4+1', field)
#a = vSpace([3,3,3,3])
#b = vSpace([0,0,0,3])
#a.logLevel = 4
c = vSpace('(z+1)*x^3+x^2+x+(z)')
c.logLevel = 4
print c
~c