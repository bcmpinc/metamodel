
root=MetaModel()

net=Element(of=root, name="Petrinet")
place=Element(of=root, name="Place")
transition=Element(of=root, name="Transition")
inedge=Element(of=root, name="ToTransition")
outedge=Element(of=root, name="FromTransition")

Attribute(of=place, name="name")
Attribute(of=place, name="capacity")
Attribute(of=place, name="tokens")
Attribute(of=inedge, name="weight")
Attribute(of=outedge, name="weight")

Relation(parent=net, child=place, name="of", listname="places")
Relation(parent=net, child=transition, name="of", listname="transitions")
Relation(parent=place, child=inedge, name="source", listname="totransitions")
Relation(parent=transition, child=inedge, name="dest", listname="fromplaces")
Relation(parent=transition, child=outedge, name="source", listname="toplaces")
Relation(parent=place, child=outedge, name="dest", listname="fromtransitions")
