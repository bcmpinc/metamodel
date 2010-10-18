
root=MetaModel()

graph=Element(of=root, name="MetaModel")
element=Element(of=root, name="Element")
attribute=Element(of=root, name="Attribute")
association=Element(of=root, name="Association")

Attribute(of=element, name="name")
Attribute(of=attribute, name="name")
Attribute(of=association, name="name")
Attribute(of=association, name="listname")

Association(parent=element, child=association, name="parent", listname="childlist")
Association(parent=element, child=association, name="child", listname="parents")
Association(parent=element, child=attribute, name="of", listname="attributes")
Association(parent=graph, child=element, name="of", listname="elements")

