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
        
        netin.identifiers = dict(root=netin.identifiers["root"])
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
        with self.assertRaisesRegexp(KeyError, "Redefinition of Element"):
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'Element(of=root, name="Duplicate")\n'
                'Element(of=root, name="Duplicate")\n'
            )

    def test_duplicate_field_attribute(self):
        with self.assertRaisesRegexp(KeyError, "Redefinition of field"):
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'Attribute(of=el, name="duplicate")\n'
                'Attribute(of=el, name="duplicate")\n'
            )

    def test_duplicate_field_subclass_attribute_1(self):
        with self.assertRaisesRegexp(KeyError, "Redefinition of field"):
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'subel = Element(of=root, name="SubTest", extends=el)\n'
                'Attribute(of=el, name="duplicate")\n'
                'Attribute(of=subel, name="duplicate")\n'
            )

    def test_duplicate_field_subclass_attribute_2(self):
        with self.assertRaisesRegexp(KeyError, "Redefinition of field"):
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'subel = Element(of=root, name="SubTest", extends=el)\n'
                'Attribute(of=subel, name="duplicate")\n'
                'Attribute(of=el, name="duplicate")\n'
            )

    def test_duplicate_field_subclass_attribute_3(self):
        with self.assertRaisesRegexp(KeyError, "Redefinition of field"):
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'Attribute(of=el, name="duplicate")\n'
                'subel = Element(of=root, name="SubTest", extends=el)\n'
                'Attribute(of=subel, name="duplicate")\n'
            )

    def test_duplicate_field_parent(self):
        with self.assertRaisesRegexp(KeyError, "Redefinition of field"):
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'el2 = Element(of=root, name="Test2")\n'
                'Association(parent=el, child=el2, parentname="duplicate", childname="dummy1")\n'
                'Association(parent=el, child=el2, parentname="duplicate", childname="dummy2")\n'
            )

    def test_duplicate_field_childlist(self):
        with self.assertRaisesRegexp(KeyError, "Redefinition of field"):
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'el2 = Element(of=root, name="Test2")\n'
                'Association(parent=el, child=el2, parentname="dummy1", childname="duplicate")\n'
                'Association(parent=el, child=el2, parentname="dummy2", childname="duplicate")\n'
            )

    def test_duplicate_field_self_reference(self):
        with self.assertRaisesRegexp(AttributeError, "Can't use the same names when defining a self-association"):
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'Association(parent=el, child=el, parentname="duplicate", childname="duplicate", optional=True)\n'
            )

    def test_underscore_field_attribute(self):
        with self.assertRaisesRegexp(AttributeError, "Attributes can not start with an underscore"):
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'Attribute(of=el, name="_duplicate")\n'
            )

    def test_underscore_field_parent(self):
        with self.assertRaisesRegexp(AttributeError, "Association parent names can not start with an underscore"):
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'Association(parent=el, child=el, parentname="_wrong", childname="good", optional=True)\n'
            )

    def test_underscore_field_child_list(self):
        with self.assertRaisesRegexp(AttributeError, "Association child names can not start with an underscore"):
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'Association(parent=el, child=el, parentname="good", childname="_wrong", optional=True)\n'
            )

    def test_unsatisfiable_self_association_constraint(self):
        with self.assertRaisesRegexp(AttributeError, "Self-associations must be optional"):
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = el2 = Element(of=root, name="Test")\n'
                'Association(parent=el, child=el2, parentname="a", childname="b", optional=False)\n'
            )

    @unittest.expectedFailure
    def test_unsatisfiable_cyclic_association_constraint(self):
        with self.assertRaisesRegexp(AttributeError, "Required associations can not be cyclic"):
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'el2 = Element(of=root, name="Test2")\n'
                'Association(parent=el, child=el2, parentname="a", childname="b", optional=False)\n'
                'Association(parent=el2, child=el, parentname="c", childname="d", optional=False)\n'
            )

    @unittest.expectedFailure
    def test_unsatisfiable_cyclic_association_constraint_3(self):
        with self.assertRaisesRegexp(AttributeError, "Required associations can not be cyclic"):
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'el2 = Element(of=root, name="Test2")\n'
                'el3 = Element(of=root, name="Test3")\n'
                'Association(parent=el, child=el2, parentname="a", childname="b", optional=False)\n'
                'Association(parent=el2, child=el3, parentname="c", childname="d", optional=False)\n'
                'Association(parent=el3, child=el, parentname="e", childname="f", optional=False)\n'
            )

    def test_negative_association_limit(self):
        with self.assertRaisesRegexp(AttributeError, "Limit '.*' must be a positive integer"):
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'el2 = Element(of=root, name="Test2")\n'
                'Association(parent=el, child=el2, parentname="a", childname="b", limit=-15)\n'
            )

    def test_zero_association_limit(self):
        with self.assertRaisesRegexp(AttributeError, "Limit '.*' must be a positive integer"):
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'el2 = Element(of=root, name="Test2")\n'
                'Association(parent=el, child=el2, parentname="a", childname="b", limit=0)\n'
            )

    def test_association_limit_as_string(self):
        with self.assertRaisesRegexp(AttributeError, "Limit '.*' must be a positive integer"):
            metamodel.MetaModel(
                'root = MetaModel()\n'
                'el = Element(of=root, name="Test")\n'
                'el2 = Element(of=root, name="Test2")\n'
                'Association(parent=el, child=el2, parentname="a", childname="b", limit="2")\n'
            )


class InstanceErrors(unittest.TestCase):
    """Test whether instance creation will raise errors when necessary."""
    
    def setUp(self):
        self.instance=metamodel.MetaModel(
            'root = MetaModel()\n'
            'el = Element(of=root, name="Test")\n'
            'Element(of=root, name="SubTest", extends=el)\n'
            'el2 = Element(of=root, name="Test2")\n'
            'Element(of=root, name="SubTest2", extends=el2)\n'
            'Attribute(of=el, name="attr")\n'
            'Association(parent=el, child=el2, parentname="a", childname="a", limit=2)\n'
            'Association(parent=el, child=el2, parentname="b", childname="b", optional=True)\n'
        ).instance()

    def test_set_unknown_attribute(self):
        with self.assertRaisesRegexp(AttributeError, "Unknown Attribute 'unknown'"):
            self.instance.parse(
                'root = Test(unknown=3)\n'
            )

    def test_get_unknown_attribute(self):
        self.instance.parse(
            'root = Test()\n'
        )
        with self.assertRaisesRegexp(AttributeError, "Unknown Attribute 'unknown'"):
            self.instance.identifiers["root"].unknown

    def test_known_attribute(self):
        self.instance.parse(
            'root = Test(attr=3)\n'
        )
        self.assertEqual(self.instance.identifiers["root"].attr, 3)
        self.instance.identifiers["root"].attr=4
        self.assertEqual(self.instance.identifiers["root"].attr, 4)

    def test_subclass_attribute(self):
        self.instance.parse(
            'root = SubTest(attr=3)\n'
        )
        self.assertEqual(self.instance.identifiers["root"].attr, 3)
        self.instance.identifiers["root"].attr=4
        self.assertEqual(self.instance.identifiers["root"].attr, 4)

    def test_set_child_list(self):
        self.instance.parse(
            'root = Test()\n'
        )
        with self.assertRaisesRegexp(AttributeError, "Setting value of childlist 'a'"):
            self.instance.identifiers["root"].a=2

    def test_create_child_good(self):
        self.instance.parse(
            'root = Test()\n'
            'Test2(a=root, b=root)\n'
        )

    def test_create_child_optional(self):
        self.instance.parse(
            'root = Test()\n'
            'Test2(a=root)\n'
        )

    def test_create_child_of_subclass(self):
        self.instance.parse(
            'root = SubTest()\n'
            'Test2(a=root)\n'
        )

    def test_create_child_wrong_type(self):
        with self.assertRaisesRegexp(AttributeError, "which is not an"):
            self.instance.parse(
                'root = Test()\n'
                't = Test2(a=root, b=root)\n'
                'Test2(a=root, b=t)\n'
            )

    def test_create_child_missing_required_parent(self):
        with self.assertRaisesRegexp(AttributeError, r"No parents specified for association\(s\)"):
            self.instance.parse(
                'root = Test()\n'
                't = Test2()\n'
            )

    def test_create_subclass_child_missing_required_parent(self):
        with self.assertRaisesRegexp(AttributeError, r"No parents specified for association\(s\)"):
            self.instance.parse(
                'root = SubTest2()\n'
            )

    def test_create_child_exceed_limit(self):
        with self.assertRaisesRegexp(KeyError, "to exceed its limit"):
            self.instance.parse(
                'root = Test()\n'
                'Test2(a=root)\n'
                'Test2(a=root)\n'
                'Test2(a=root)\n'
            )

            
if __name__ == '__main__':
    unittest.main()
