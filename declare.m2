root = MetaModel()
diagram = Element(of=root, name="DeclareDiagram")


# Activity element
act = Element(of=root, name="Activity")
Association(parent=diagram, child=act, parentname="of", childname="activities")
Attribute(of=act, name="init")
Attribute(of=act, name="existence")
Attribute(of=act, name="absence")
Attribute(of=act, name="name")


# Binary relations
bin = Element(of=root, name="BinaryRelation", abstract=True)
Association(parent=act, child=bin, parentname="left", childname="relatedright")
Association(parent=act, child=bin, parentname="right", childname="relatedleft")

Element(of=root, name="RespondedExistence", extends=bin)
Element(of=root, name="CoExistence", extends=bin)
Element(of=root, name="Response", extends=bin)
Element(of=root, name="Precedence", extends=bin)
Element(of=root, name="Succession", extends=bin)
Element(of=root, name="AlternateResponse", extends=bin)
Element(of=root, name="AlternatePrecedence", extends=bin)
Element(of=root, name="AlternateSuccession", extends=bin)
Element(of=root, name="ChainResponse", extends=bin)
Element(of=root, name="ChainPrecedence", extends=bin)
Element(of=root, name="ChainSuccession", extends=bin)
Element(of=root, name="NotCoExistence", extends=bin)
Element(of=root, name="NotSuccession", extends=bin)
Element(of=root, name="NotChainSuccession", extends=bin)


# N-ary relation
nary = Element(of=root, name="NAryRelation", abstract=True)
Association(parent=diagram, child=nary, parentname="of", childname="relations")
part = Element(of=root, name="Participation")
Association(parent=act, child=part, parentname="activity", childname="relatedwith")
Association(parent=nary, child=part, parentname="relation", childname="contains")

Element(of=root, name="Choice", extends=nary)
Element(of=root, name="Exclusive", extends=nary)
Attribute(of=nary, name="count")

