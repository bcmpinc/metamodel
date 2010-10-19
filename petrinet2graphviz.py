#!/usr/bin/python3
#
# Converts petrinets to graphviz graphs.
# Copyright (C) 2010  Bauke Conijn
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os

if len(sys.argv)==1:
    sys.argv.append("-")
if len(sys.argv)!=2 or not (sys.argv[1]=="-" or os.path.isfile(sys.argv[1])):
    print("Usage: {0} [filename.m1|-]".format(sys.argv[0]))
    sys.exit(1)

import metamodel

net = metamodel.load("petrinets.m2")
netin = net.instance().load(sys.argv[1])

@metamodel.TransformationRule
def petrinet2graphviz(petrinet):
    global transitioncount
    transitioncount=0
    r = ["digraph {"]
    r.append("// Places:")
    for place in petrinet.places:
        r.append(place2graphviz(place))
    r.append("\n// Transitions:")
    for transition in petrinet.transitions:
        r.append(transition2graphviz(transition))
    r.append("\n// Edges:")
    for place in petrinet.places:
        for edge in place.totransitions:
            inedge2graphviz(edge, r)
        for edge in place.fromtransitions:
            outedge2graphviz(edge, r)
    r.append("}\n")
    return "\n".join(r)

@metamodel.TransformationRule
def place2graphviz(place):
    return '{0} [shape=circle];'.format(place.name)

@metamodel.TransformationRule
def transition2graphviz(transition):
    return '{0} [shape=box, label=""];'.format(transition2name(transition))
    
@metamodel.TransformationRule
def transition2name(transition):
    global transitioncount
    transitioncount += 1
    return "T_{0}".format(transitioncount)

@metamodel.TransformationRule
def inedge2graphviz(edge, r):
    a=[]
    if edge.weight!=None and edge.weight!=1:
        a.append('label="{0}"'.format(edge.weight))
    r.append("{0} -> {1} [{2}];".format(edge.source.name, transition2name(edge.dest), ",".join(a)))
    
@metamodel.TransformationRule
def outedge2graphviz(edge, r):
    a=[]
    if edge.weight!=None and edge.weight!=1:
        a.append('label="{0}"'.format(edge.weight))
    r.append("{0} -> {1} [{2}];".format(transition2name(edge.source), edge.dest.name, ",".join(a)))
    

print(petrinet2graphviz(netin.root()))
