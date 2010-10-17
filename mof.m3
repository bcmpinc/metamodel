
root=MetaModel()

graph=Element(of=root, name="MetaModel")
element=Element(of=root, name="Element")
attribute=Element(of=root, name="Attribute")
relation=Element(of=root, name="Relation")

Attribute(of=element, name="name")
Attribute(of=attribute, name="name")
Attribute(of=relation, name="name")
Attribute(of=relation, name="listname")

Relation(parent=element, child=relation, name="parent", listname="childlist")
Relation(parent=element, child=relation, name="child", listname="parents")
Relation(parent=element, child=attribute, name="of", listname="attributes")
Relation(parent=graph, child=element, name="of", listname="elements")

