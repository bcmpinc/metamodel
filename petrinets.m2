
root=MetaModel()

net=Element(of=root, name="Petrinet")
place=Element(of=root, name="Place")
transition=Element(of=root, name="Transition")
iplace=Element(of=root, name="InterfacePlace", extends=place)
itransition=Element(of=root, name="InterfaceTransition", extends=transition)
inedge=Element(of=root, name="ToTransition")
outedge=Element(of=root, name="FromTransition")

Attribute(of=iplace, name="name")
Attribute(of=itransition, name="name")
Attribute(of=place, name="capacity")
Attribute(of=place, name="tokens")
Attribute(of=inedge, name="weight")
Attribute(of=outedge, name="weight")

Association(parent=net, child=place, parentname="of", childname="places")
Association(parent=net, child=transition, parentname="of", childname="transitions")
Association(parent=place, child=inedge, parentname="source", childname="totransitions")
Association(parent=transition, child=inedge, parentname="dest", childname="fromplaces")
Association(parent=transition, child=outedge, parentname="source", childname="toplaces")
Association(parent=place, child=outedge, parentname="dest", childname="fromtransitions")
