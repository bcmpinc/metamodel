#!/usr/bin/python3
#
# Removes InterfacePlaces and InterfaceTransitions from petrinets.
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
def skeleton(source):
    r = net.instance()
    r.identifiers["root"]=petrinet(source.root())
    return r
    
@metamodel.TransformationRule
def petrinet(root):
    for element in root.places:
        copy_non_interface.later(element)
    for element in root.transitions:
        copy_non_interface.later(element)
    return M.Petrinet()

@metamodel.TransformationRule
def copy_non_interface(element):
    if element.__class__ == M.Place:
        for edge in element.totransitions:
            copy_edge.later(edge)
        for edge in element.fromtransitions:
            copy_edge.later(edge)
        return M.Place(of=petrinet(element.of), capacity=element.capacity, tokens=element.tokens)
    elif element.__class__ == M.Transition:
        return M.Transition(of=petrinet(element.of))
    else:
        return None

@metamodel.TransformationRule
def copy_edge(element):
    source = copy_non_interface(element.source)
    dest = copy_non_interface(element.dest)
    if source==None or dest==None:
        return None
    else:
        return element.__class__(source=source, dest=dest, weight=element.weight)

print(skeleton(netin))
