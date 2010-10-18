#!/usr/bin/python3

import metamodel

net = metamodel.load("petrinets.m2")
print(net)
netin = net.instance().load("petrinet.m1")
netin.identifiers=dict()
print(netin)
print()
mof = metamodel.load("mof.m3")
print(mof)
print()
print(mof.instance().load("petrinets.m2"))
print()
print(mof.instance().load("mof.m3"))

mof.instance().load("mof.m3").save("moftest.m2")
    
print(metamodel.load("moftest.m2"))

from os import unlink
unlink("moftest.m2")
