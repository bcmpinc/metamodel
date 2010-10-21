
root=MetaModel()


absnet=Element(of=root, name="AbstractPetrinet", abstract=True)

comp=Element(of=root, name="Composition", abstract=True, extends=absnet)
sync=Element(of=root, name="Sync", extends=comp)
async=Element(of=root, name="Async", extends=comp)

net=Element(of=root, name="Petrinet", extends=absnet)
place=Element(of=root, name="Place")
transition=Element(of=root, name="Transition")
iplace=Element(of=root, name="InterfacePlace", extends=place)
itransition=Element(of=root, name="InterfaceTransition", extends=transition)
inedge=Element(of=root, name="InputArc")
outedge=Element(of=root, name="OutputArc")

Attribute(of=net, name="name")
Attribute(of=place, name="name")
Attribute(of=transition, name="name")
Attribute(of=place, name="capacity")
Attribute(of=place, name="tokens")
Attribute(of=inedge, name="weight")
Attribute(of=outedge, name="weight")

Association(parent=comp, child=absnet, parentname="of", childname="composes", optional=True)

Association(parent=net, child=place, parentname="of", childname="places")
Association(parent=net, child=transition, parentname="of", childname="transitions")
Association(parent=place, child=inedge, parentname="source", childname="totransitions")
Association(parent=transition, child=inedge, parentname="dest", childname="fromplaces")
Association(parent=transition, child=outedge, parentname="source", childname="toplaces")
Association(parent=place, child=outedge, parentname="dest", childname="fromtransitions")
