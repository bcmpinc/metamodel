
root=MetaModel()

graph=Element(of=root, name="MetaModel")
element=Element(of=root, name="Element")
attribute=Element(of=root, name="Attribute")
association=Element(of=root, name="Association")

Attribute(of=element, name="name")
Attribute(of=element, name="abstract")
Attribute(of=attribute, name="name")
Attribute(of=association, name="parentname")
Attribute(of=association, name="childname")
Attribute(of=association, name="limit")
Attribute(of=association, name="optional")

Association(parent=element, child=association, parentname="parent", childname="childlist")
Association(parent=element, child=association, parentname="child", childname="parents")
Association(parent=element, child=attribute, parentname="of", childname="attributes")
Association(parent=graph, child=element, parentname="of", childname="elements")
Association(parent=element, child=element, parentname="extends", childname="subclasses", optional=True)

