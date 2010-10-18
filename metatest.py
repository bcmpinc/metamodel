#!/usr/bin/python3

import metamodel

net = metamodel.load("petrinets.m3")
print(net)
netin = net.instance().load("petrinet.m2")
netin.identifiers=dict()
print(netin)
print()
mof = metamodel.load("mof.m3")
print(mof)
print()
print(mof.instance().load("petrinets.m3"))
print()
print(mof.instance().load("mof.m3"))

mof.instance().load("mof.m3").save("moftest.m3")
    
print(metamodel.load("moftest.m3"))
