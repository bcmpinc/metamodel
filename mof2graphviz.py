#!/usr/bin/python3
#
# Converts metamodels to graphviz graphs.
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

net = metamodel.load("mof.m3")
netin = net.instance().load(sys.argv[1])

@metamodel.TransformationRule
def metamodel2graphviz(metamodel):
    global attributecount, associationcount
    attributecount=0
    associationcount=0
    r = ["digraph {", "overlap=false;", "splines=true;", "edge[fontsize=12, len=1];", "model=mds;"]
    r.append("// Elements:")
    for element in metamodel.elements:
        element2graphviz(element, r)

    r.append("\n// Associations:")
    for element in metamodel.elements:
        for a in element.childlist:
            association2graphviz(a, r)

    r.append("}\n")
    return "\n".join(r)

@metamodel.TransformationRule
def element2graphviz(element, r):
    if element.extends!=None:
        r.append('{1}:T -> {0}:T [arrowtail=onormal, dir=back, len=.5];'.format(element.name, element.extends.name))
    if len(element.attributes) > 0:
        attrlist = '<TR><TD ALIGN="LEFT" BALIGN="LEFT"><FONT POINT-SIZE="12">{0}</FONT></TD></TR>'.format(r"<BR/>".join([a.name for a in element.attributes]))
    else:
        attrlist = ""
    if element.abstract:
        name = '<FONT FACE="italic">{0}</FONT>'.format(element.name)
    else:
        name = element.name
    label = '<<TABLE PORT="T" BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD>{0}</TD></TR>{1}</TABLE>>'.format(name, attrlist)
    r.append('{0} [shape=none, label={1}];'.format(element.name, label))
    r.append("")

@metamodel.TransformationRule
def association2graphviz(a, r):
    global associationcount
    associationcount += 1
    dummy="_assoc_{0}".format(associationcount)
    r.append(r'{0} [shape=point, label="", width=0, height=0]'.format(dummy))
    r.append(r'{0}:T -> {1} [arrowtail=vee, dir=back, label="{2}\n{3}", len=.3];'.format(
        a.parent.name, dummy, 
        a.parentname, "0..1" if a.optional else "1",
    ))
    r.append(r'{0} -> {1}:T [dir=none, label="{2}\n{3}", len=.3];'.format(
        dummy, a.child.name, 
        a.childname, "0..{0}".format(a.limit) if a.limit!=None else "*", 
    ))
    r.append(r'{0}:T -> {1}:T [color=none, len=1.4];'.format(
        a.parent.name, a.child.name,
    ))

print(metamodel2graphviz(netin.root()))
