#!/usr/bin/python3

import metamodel

net = metamodel.load("petrinets.m3")
print(net)
netin = net.load("petrinet.m2")
netin.identifiers=dict()
print(netin)
print()
mof = metamodel.load("mof.m3")
print(mof)
print()
print(mof.load("petrinets.m3"))
print()
print(mof.load("mof.m3"))
