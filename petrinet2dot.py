#!/usr/bin/python3

import metamodel

net = metamodel.load("petrinets.m3")
print(net)
print(net.load("petrinet.m2"))

mof = metamodel.load("mof.m3")
print(mof)
mof.load("petrinets.m3")
mof.load("mof.m3")
