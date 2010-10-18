#!/usr/bin/python3

import metamodel
import unittest

class IntegrationTests(unittest.TestCase):
    """Some tests that test whether the whole system works together."""
    
    def test_petrinet(self):
        net = metamodel.load("petrinets.m2")
        modeldesc = str(net).split("\n")
        self.assertTrue("  Element Place" in modeldesc)
        self.assertTrue("    <attribute> name" in modeldesc)
        self.assertTrue("    FromTransition[] fromtransitions" in modeldesc)
        
        netin = net.instance().load("petrinet.m1")
        repr(netin)
        
        netin.identifiers=dict()
        repr(netin)
            
    def test_mof(self):
        mof = metamodel.load("mof.m3")
        modeldesc = str(mof).split("\n")
        self.assertTrue("    Element extends (optional)" in modeldesc)
        self.assertTrue("  Element MetaModel" in modeldesc)
        self.assertTrue("    <attribute> limit" in modeldesc)
        
        net = mof.instance().load("petrinets.m2")
        repr(net)
        mofi = mof.instance().load("mof.m3")
        mofdesc = repr(mofi)
        
        mof2 = metamodel.MetaModel(mofdesc)
        mofi2 = mof2.instance().parse(mofdesc)

class ModelErrors(unittest.TestCase):
    """Test that errors in a meta model are detected."""
    
    def test_duplicate_element(self):
        with self.assertRaisesRegexp(KeyError, "Redefinition of Element") as cm:
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'Element(of=root, name="Duplicate")\n'
                'Element(of=root, name="Duplicate")\n'
            )

    def test_duplicate_field_attribute(self):
        with self.assertRaisesRegexp(KeyError, "Redefinition of field") as cm:
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'Attribute(of=el, name="duplicate")\n'
                'Attribute(of=el, name="duplicate")\n'
            )

    def test_duplicate_field_parent(self):
        with self.assertRaisesRegexp(KeyError, "Redefinition of field") as cm:
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'el2 = Element(of=root, name="Test2")\n'
                'Association(parent=el, child=el2, parentname="duplicate", childname="dummy1")\n'
                'Association(parent=el, child=el2, parentname="duplicate", childname="dummy2")\n'
            )

    def test_duplicate_field_childlist(self):
        with self.assertRaisesRegexp(KeyError, "Redefinition of field") as cm:
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'el2 = Element(of=root, name="Test2")\n'
                'Association(parent=el, child=el2, parentname="dummy1", childname="duplicate")\n'
                'Association(parent=el, child=el2, parentname="dummy2", childname="duplicate")\n'
            )

    def test_duplicate_field_self_reference(self):
        with self.assertRaisesRegexp(AttributeError, "Can't use the same names when defining a self-association") as cm:
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'Association(parent=el, child=el, parentname="duplicate", childname="duplicate", optional=True)\n'
            )

    def test_underscore_field_attribute(self):
        with self.assertRaisesRegexp(AttributeError, "Attributes can not start with an underscore") as cm:
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'Attribute(of=el, name="_duplicate")\n'
            )

    def test_underscore_field_attribute(self):
        with self.assertRaisesRegexp(AttributeError, "Attributes can not start with an underscore") as cm:
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'Attribute(of=el, name="_duplicate")\n'
            )

    def test_underscore_field_attribute(self):
        with self.assertRaisesRegexp(AttributeError, "Attributes can not start with an underscore") as cm:
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'Attribute(of=el, name="_duplicate")\n'
            )

    def test_unsatisfiable_association_constraint(self):
        with self.assertRaisesRegexp(AttributeError, "Self-associations must be optional") as cm:
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = el2 = Element(of=root, name="Test")\n'
                'Association(parent=el, child=el2, parentname="a", childname="b", optional=False)\n'
            )

    def test_negative_association_limit(self):
        with self.assertRaisesRegexp(AttributeError, "Limit '.*' must be positive") as cm:
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'el2 = Element(of=root, name="Test2")\n'
                'Association(parent=el, child=el2, parentname="a", childname="b", limit=-15)\n'
            )

    def test_zero_association_limit(self):
        with self.assertRaisesRegexp(AttributeError, "Limit '.*' must be positive") as cm:
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'el2 = Element(of=root, name="Test2")\n'
                'Association(parent=el, child=el2, parentname="a", childname="b", limit=0)\n'
            )

    def test_association_limit_as_string(self):
        with self.assertRaisesRegexp(AttributeError, "Limit '.*' must be positive") as cm:
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'el2 = Element(of=root, name="Test2")\n'
                'Association(parent=el, child=el2, parentname="a", childname="b", limit="2")\n'
            )


class InstanceErrors(unittest.TestCase):
    def setUp(self):
        self.instance=MetaModel(
            'root = '
        ).instance()


if __name__ == '__main__':
    unittest.main()
