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

net = metamodel.load("declare.m2")
netin = net.instance().load(sys.argv[1])

M=type("DeclareModel", (), net.elements)

@metamodel.TransformationRule
def declare2graphviz(declare):
    global activitycount, relationcount, negatecount
    activitycount=0
    relationcount=0
    negatecount=0
    r = ["digraph {", "overlap=false;", "splines=true;", "model=mds"]
    r.append("// Activities:")
    for activity in declare.activities:
        activity2graphviz(activity, r)
    r.append("// Binary Relations:")
    for activity in declare.activities:
        for binary in activity.relatedleft:
            binary2graphviz(binary, r)
    r.append("// N-ary Relations:")
    for relation in declare.relations:
        relation2graphviz(relation, r)
    
    r.append("}\n")
    return "\n".join(r)

@metamodel.TransformationRule
def activity2graphviz(activity,r):
    global activitycount
    tag = "A{0}".format(activitycount)
    activitycount += 1
    r.append('{0} [shape=none, label=<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0">'.format(tag))
    if activity.init:
        r.append('<TR><TD></TD><TD BORDER="1">init</TD><TD></TD></TR>')
    lowerbound = activity.existence if activity.existence!=None else 0
    upperbound = activity.absence-1 if activity.absence!=None else "*"
    if lowerbound==upperbound:
        r.append('<TR><TD></TD><TD BORDER="1">{0}</TD><TD></TD></TR>'.format(lowerbound))
    elif lowerbound!=0 or upperbound!="*":
        r.append('<TR><TD></TD><TD BORDER="1">{0}..{1}</TD><TD></TD></TR>'.format(lowerbound, upperbound))
    r.append('<TR><TD BORDER="1" COLSPAN="3" CELLPADDING="10" PORT="T">{0}</TD></TR>'.format(activity.name))
    r.append('</TABLE>>];') 
    return tag

@metamodel.TransformationRule
def relation2graphviz(relation, r):
    global relationcount
    tag = "R{0}".format(relationcount)
    relationcount += 1
    n = relation.count if relation.count != None else 1
    label = r'{0} of {1}'.format(n, len(relation.contains))
    if isinstance(relation, M.Choice):
        r.append('{0} [shape=diamond, label="{1}", fontsize=12];'.format(tag, label))
    elif isinstance(relation, M.Exclusive):
        r.append('{0} [shape=diamond, label="{1}", fontsize=12, style="filled", fillcolor="black", fontcolor="white", fontname="bold"];'.format(tag, label))
    for participation in relation.contains:
        r.append('{0}:T->{1} [dir=none];'.format(activity2graphviz(participation.activity), tag))
    return tag
    
binarystyles = {
    #                       left    right     negation lines
    M.RespondedExistence:  ("dot",  "none",      False, 1),
    M.CoExistence:         ("dot",  "dot",       False, 1),
    
    M.Precedence:          ("none", "dotnormal", False, 1),
    M.Response:            ("dot",  "normal",    False, 1),
    M.Succession:          ("dot",  "dotnormal", False, 1),
    
    M.AlternateResponse:   ("none", "dotnormal", False, 2),
    M.AlternatePrecedence: ("dot",  "normal",    False, 2),
    M.AlternateSuccession: ("dot",  "dotnormal", False, 2),
    
    M.ChainResponse:       ("none", "dotnormal", False, 3),
    M.ChainPrecedence:     ("dot",  "normal",    False, 3),
    M.ChainSuccession:     ("dot",  "dotnormal", False, 3),
    
    M.NotCoExistence:      ("dot",  "dot",       True,  1),
    M.NotSuccession:       ("dot",  "dotnormal", True,  1),
    M.NotChainSuccession:  ("dot",  "dotnormal", True,  3),
}
    
@metamodel.TransformationRule
def binary2graphviz(binary, r):
    left =activity2graphviz(binary.left)+":T"
    right=activity2graphviz(binary.right)+":T"
    try:
        style = binarystyles[binary.__class__]
        color = ":".join(["black"]*style[3])
        if style[2]:
            # Negation
            global negatecount
            tag = "N{0}".format(negatecount)
            negatecount += 1
            r.append('{0} -> {1} [arrowtail="{2[0]}", arrowhead="tee", color="{3}", dir=both, len=.8];'.format(left, tag, style, color))
            r.append('{0} -> {1} [arrowtail="tee", arrowhead="{2[1]}", color="{3}", dir=both, len=.8];'.format(tag, right, style, color))
            r.append('{0} [shape=point, label="", width=0, height=0];'.format(tag))
        else:
            r.append('{0} -> {1} [arrowtail="{2[0]}", arrowhead="{2[1]}", color="{3}", dir=both, len=1.5];'.format(left, right, style, color))
            
    except KeyError:
        r.append('{0} -> {1} [color=red, len=1.5, label="{2}"];'.format(left, right, binary.__class__.__name__))

print(declare2graphviz(netin.root()))
