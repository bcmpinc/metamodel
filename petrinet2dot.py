#!/usr/bin/python3

import sys
import os

if len(sys.argv)!=2 or not os.path.isfile(sys.argv[1]):
    print("Usage: {0} filename.m1".format(sys.argv[0]))
    sys.exit(1)

import metamodel

net = metamodel.load("petrinets.m2")
netin = net.instance().load(sys.argv[1])

@metamodel.TransformationRule
def petrinet2dot(petrinet):
    global transitioncount
    transitioncount=0
    r = linelist(petrinet)
    r.append("// Places:")
    for place in petrinet.places:
        r.append(place2dot(place))
    r.append("\n// Transitions:")
    for transition in petrinet.transitions:
        r.append(transition2dot(transition))
    r.append("\n// Edges:")
    for place in petrinet.places:
        for edge in place.totransitions:
            inedge2dot(edge, r)
        for edge in place.fromtransitions:
            outedge2dot(edge, r)
    r.append("}\n")
    return "\n".join(r)

@metamodel.TransformationRule
def linelist(petrinet):
    return ["digraph {"]

@metamodel.TransformationRule
def place2dot(place):
    return '{0} [shape=circle];'.format(place.name)

@metamodel.TransformationRule
def transition2dot(transition):
    return '{0} [shape=box, label=""];'.format(transition2name(transition))
    
@metamodel.TransformationRule
def transition2name(transition):
    global transitioncount
    transitioncount += 1
    return "T_{0}".format(transitioncount)

@metamodel.TransformationRule
def inedge2dot(edge, r):
    a=[]
    if edge.weight!=None and edge.weight!=1:
        a.append('label="{0}"'.format(edge.weight))
    r.append("{0} -> {1} [{2}];".format(edge.source.name, transition2name(edge.dest), ",".join(a)))
    
@metamodel.TransformationRule
def outedge2dot(edge, r):
    a=[]
    if edge.weight!=None and edge.weight!=1:
        a.append('label="{0}"'.format(edge.weight))
    r.append("{0} -> {1} [{2}];".format(transition2name(edge.source), edge.dest.name, ",".join(a)))
    

print(petrinet2dot(netin.root()))
