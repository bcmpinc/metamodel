#!/usr/bin/python3

import metamodel

net = metamodel.load("petrinets.m2")
print(net)
netin = net.load("petrinet.m1")

print(netin)

def petrinet2dot(petrinet):
    
