#!/usr/bin/env python

##############################################################################
##
## file: armor.py
##
## developers history & copyleft: Sergi Blanch-Torne
##
## Copyright 2011, 2012, 2013, 2014 (copyleft)
## 
## This file is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## This file is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with this file.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

#base32 = {}
#for i in range(0,10):
#    base32['%d'%i] = i
#l = 'abcdfghjklmnpqrstvwxyz'#len 22
#p = []
#for e in l:
#    p.append(e)
#for i,e in enumerate(p):
#    base32[e] = i+10
base32 = {'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,
         'a':10,'b':11,'c':12,'d':13,'f':14,'g':15,'h':16,'j':17,'k':18,'l':19,
         'm':20,'n':21,'p':22,'q':23,'r':24,'s':25,'t':26,'v':27,'w':28,'x':29,
         'y': 30,'z':31
        }
#inv32 = {}
#for k in mod32.keys():
#    inv32[mod32[k]] = k
inv32 = {0:'0',1:'1',2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',
         10:'a',11:'b',12:'c',13:'d',14:'f',15:'g',16:'h',17:'j',18:'k',19:'l',
         20:'m',21:'n',22:'p',23:'q',24:'r',25:'s',26:'t',27:'v',28:'w',29:'x',
         30:'y',31:'z'
        }


class Armor32:
    def __init__(self):
        pass
    def encode(self,integer):
        string = ""
        mask = 0b11111
        while not integer == 0:
            element = integer & mask
            string = "%s%s"%(inv32[element],string)
            integer = integer >> 5
        return string
    def decode(self,string):
        string = string.lower()
        integer = 0
        for element in string:
            integer = integer << 5
            integer += base32[element]
        return integer

base36 = {'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,
          'a':10,'b':11,'c':12,'d':13,'e':14,'f':15,'g':16,'h':17,'i':18,'j':19,
          'k':20,'l':21,'m':22,'n':23,'o':24,'p':25,'q':26,'r':27,'s':28,'t':29,
          'u':30,'v':31,'w':32,'x':33,'y':34,'z':35
         }
inv36 = {0:'0',1:'1',2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',
         10:'a',11:'b',12:'c',13:'d',14:'e',15:'f',16:'g',17:'h',18:'i',19:'j',
         20:'k',21:'l',22:'m',23:'n',24:'o',25:'p',26:'q',27:'r',28:'s',29:'t',
         30:'u',31:'v',32:'w',33:'x',34:'y',35:'z'}

class Armor36:
    def __init__(self):
        pass
    def encode(self,integer):
        string = ""
        while integer > 36:
            string = "%s%s"%(inv36[integer % 36],string)
            integer = integer / 36
        if integer % 36 == 0:
            string = "10%s"%(string)
        else:
            string = "%s%s"%(inv36[integer % 36],string)
        return string
    def decode(self,string):
        string = string.lower()
        stringList = []
        for s in string:
            stringList.append(s)
        stringList.reverse()
        integer = 0
        for i in range(len(stringList)):
            integer += base36[stringList[i]]*(36**i)
        return integer

def main(arg0,arg1):
    if arg1 == "--help":
        print("\nBasic Usage: %s --integer=N...N|--string=X...X\n"%arg0)
        return
    armor32 = Armor32()
    armor36 = Armor36()
    command,value = arg1.split("=")
    if command == "--integer":
        if value[:2] == '0x': value = int(value,16)
        else: value = int(value)
        answer32 = armor32.encode(value)
        answer36 = armor36.encode(value)
        print("%s -> %s (base32) %s (base36)"%(value,answer32,answer36))
    elif command.startswith("--string"):
        if command.count("32"):
            answer = armor32.decode(value)
        elif command.count("36"):
            answer = armor36.decode(value)
        print("%s -> %s"%(value,answer))
    
if __name__ == "__main__":
    import sys
    import traceback
    arg0 = sys.argv[0]
    if len(sys.argv) < 2:
        arg1 = "--help"
    else:
        arg1 = sys.argv[1]
#    if len(sys.argv) == 3 and sys.argv[2] == "--debug":
#        arg2 = True
#    else:
#        arg2 = False
    try:
        main(arg0,arg1)
    except Exception,e:
        print("\nException for option %s, with reason %s\n"%(arg1,e))
        traceback.print_exc()

