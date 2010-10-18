#!/usr/bin/python3

import metamodel

net = metamodel.load("petrinets.m3")
print(net)
netin = net.load("petrinet.m2")

print(netin)

def petrinet2dot(petrinet):
    