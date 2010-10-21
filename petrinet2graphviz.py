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

M=type("PetrinetsModel", (), net.elements)

@metamodel.TransformationRule
def petrinet2graphviz(petrinet):
    global elementcount
    elementcount=0
    r = ["digraph {", "overlap=false", "model=mds"]
    r.append("// Places:")
    for place in petrinet.places:
        element2graphviz(place, r, "circle")
    r.append("\n// Transitions:")
    for transition in petrinet.transitions:
        element2graphviz(transition, r, "square")
    r.append("\n// Edges:")
    for place in petrinet.places:
        for edge in place.totransitions:
            edge2graphviz(edge, r)
        for edge in place.fromtransitions:
            edge2graphviz(edge, r)
    r.append("}\n")
    return "\n".join(r)

@metamodel.TransformationRule
def element2graphviz(element,r,shape):
    global elementcount
    a = ["shape={0}".format(shape)]
    
    tag = "place_{0}".format(elementcount)
    nametag = "cluster_p{0}".format(elementcount)
    elementcount += 1
    if element.name!=None and element.name!="":
        r.append('subgraph {0} {{ label="{1}"; color=none; fontsize=12;'.format(nametag, element.name))
    if isinstance(element, M.InterfacePlace) or isinstance(element, M.InterfaceTransition):
        a.append('penwidth=3')
    
    a.append('fixedsize=true')
    a.append('color=black')
    if hasattr(element, "tokens"):
        if element.tokens<6:
            a.append('label="{0}"'.format(["","·",":","∴","∷","⁙"][element.tokens]))
            a.append('fontsize=32')
        else:
            a.append('label="{0}"'.format(element.tokens))
    else:
        a.append('label=""')
        
    r.append('{0} [{1}];'.format(tag, ",".join(a)))
    if element.name!=None and element.name!="":
        r.append('}')
    return tag

@metamodel.TransformationRule
def edge2graphviz(edge, r):
    a=["len=1"]
    if edge.weight!=None and edge.weight!=1:
        a.append('label="{0}"'.format(edge.weight))
    r.append("{0} -> {1} [{2}];".format(element2graphviz(edge.source), element2graphviz(edge.dest), ",".join(a)))
    

print(petrinet2graphviz(netin.root()))
