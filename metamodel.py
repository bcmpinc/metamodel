# The core of the metamodel module
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

from __future__ import print_function
import keyword
import sys
from weakref import WeakKeyDictionary


class FieldDescriptor(object):
    """Describes a field of an Element. This is an abstract class."""
    
    def __init__(self, name):
        """Creates a descriptor."""
        self.name = name
    
    def describe(self, name):
        """Used for creating a human readable description of a field."""
        return "<unknown> {1}".format(self.name)


class AttributeField(FieldDescriptor):
    """Describes an attribute of an element."""
    
    def __init__(self, name):
        FieldDescriptor.__init__(self, name)
        
    def describe(self):
        return "<attribute> {0}".format(self.name)


class ChildListField(FieldDescriptor):
    """Describes a list of references to child elements."""
    
    def __init__(self, name, parentname, elementtype, limit):
        """Creates a descriptor for the child-list field of an association.
        Parent and child-list arguments come in pairs and need 
        to be able to find each other. Therefore a 'parentname'
        argument is needed to find this field's counterpart.
        The 'elementtype' argument is used for debug output.
        The 'limit' argument limits the amount of children this
        element can have."""
        FieldDescriptor.__init__(self, name)
        self.parentname = parentname
        self.elementtype = elementtype
        self.limit = limit
        
    def describe(self):
        return "{0}[{2}] {1}".format(self.elementtype.__name__, self.name, self.limit if self.limit!=None else "")


class ParentField(FieldDescriptor):
    """Describes a reference to a parent object."""
    
    def __init__(self, name, childname, elementtype, optional):
        """Creates a descriptor for the parent field of an association.
        Parent and child-list arguments come in pairs and need 
        to be able to find each other. Therefore a 'childname'
        argument is needed to find this field's counterpart.
        For type checking the 'elementtype' is used.
        Argument 'optional' is used to make the association optional."""
        FieldDescriptor.__init__(self, name)
        self.childname = childname
        self.elementtype = elementtype
        self.optional = optional

    def describe(self):
        return "{0} {1}{2}".format(self.elementtype.__name__, self.name, " (optional)" if self.optional else "")


class AbstractElement(object):
    """The abstract base class used by elements. 
    subclasses need to define self.fields, as a
    dictionary mapping field name to FieldDescriptor."""
    
    def __init__(self, **kwargs):
        """Creates an instance of the element."""
        
        if self._abstract:
            raise RuntimeError("Can't instantiate abstract class {0}".format(self.__class__.__name__))
        
        # Create a dictionary for storing the values of the fields.
        self._values = dict()

        # Assign the values specified in the constructor.
        for (k,v) in kwargs.items():
            setattr(self,k,v)
            
        # Verify that all PARENT type attributes are set.
        err = None
        for (k,v) in self._fields.items():
            if isinstance(v, ParentField) and not v.optional and k not in self._values:
                if err == None:
                    err = []
                err.append(k)
        # Raise an error if not.
        if err != None:
            raise AttributeError("No parents specified for association(s) {0}".format(err))
                
        
    def __getattr__(self, name):
        """Returns the requested field of the element.
        If the requested field is a child-list and is not
        yet set, it is initialized with an empty set.
        This set can (but usually should not) be modified."""

        # If name start with an underscore, it is an internal attribute
        if name[0]=="_":
            return self.__dict__[name]

        # is the value set?, return it.
        if name in self._values:
            return self._values[name]
            
        # if not, check whether it actually is a valid field name.
        if name not in self._fields:
            raise AttributeError("Unknown Attribute '{0}'".format(name))
        
        # If it is a child-list, we need to initialize it first, 
        # as the return value might be modified.
        if isinstance(self._fields[name], ChildListField):
            self._values[name] = r = set()
            return r
        
        # Return the default value.
        return None
        
    def __setattr__(self, name, value):
        """Assigns value to the field name. 
        Except when the field is a child-list, because
        it can not be set."""
        
        # If name start with an underscore, it is an internal attribute
        if name[0]=="_":
            self.__dict__[name]=value
            return
        
        # Verify that name denotes a valid field name
        if name not in self._fields:
            raise AttributeError("Unknown Attribute '{0}'".format(name))
        
        # Verify that the field is not a childlist
        if isinstance(self._fields[name], ChildListField):
            raise AttributeError("Setting value of childlist '{0}'".format(name))
        
        # If a parent field is set, also update the parent's childlist and
        # do type checking.
        field = self._fields[name]
        if isinstance(field, ParentField):
            # Check that value is of the right type and raise a meaningful error otherwise.
            if not isinstance(value, field.elementtype):
                raise AttributeError("Setting '{0}' to value {1}, which is not an {2}".format(
                    name, value, field.elementtype.__name__))

            # Get a reference to the parent's childlist.
            childlist = getattr(value, field.childname)
                
            # Check of the field was already set
            if name in self._values:
                # Ignore the assignment if it does not change the value
                if id(self._values[name]) == id(self):
                    return

                # Remove the old value
                oldvalue = self._values[name]
                if oldvalue in childlist:
                    childlist.remove(oldvalue)
            
            # Check whether the parent still has room for another child.
            otherfield = value._fields[field.childname]
            if otherfield.limit!=None and len(childlist)>=otherfield.limit:
                raise KeyError("Setting {0} causes {1} to exceed its limit".format(field.describe(), otherfield.describe()))
            
            # (and) insert the new one.
            childlist.add(self)
            
        # Set the field to the new value.
        self._values[name] = value
    
    def __dir__(self):
        """Returns the field names specified by this Element."""
        return self._fields.keys()
       
       
class MetaModel:
    """The MetaModel class. Instances of this class describe 
    the structure of a model."""
    
    def __init__(self, script):
        """Creates an empty meta model."""
        
        # Create a dictionary for the different types of elements.
        self.elements=dict()
        
        # Create a dictionary in which the identifiers are stored that are used in the model description.
        self.identifiers=dict()
        
        # Create the meta-model creation environment.
        modelapi=dict(
            MetaModel=self.metamodel,
            Element=self.element,
            Attribute=self.attribute,
            Association=self.association,
        )
        
        # Load the meta-model
        exec(script, modelapi, self.identifiers)

    def metamodel(self):
        """Returns self. Used during the load process."""
        return self
    
    def element(self, of, name, extends=AbstractElement, abstract=False):
        """Adds an Element to the meta-model."""
        
        # Verify that the correct value for of is used.
        assert self is of
        
        # Verify that the element name is not yet used.
        if name in self.elements:
            raise KeyError("Redefinition of Element '{0}'".format(name))
        
        # Copy attribute dictionary of superclass
        if hasattr(extends, "_fields"):
            fields = dict(extends._fields)
            # The copy here can be made while not yet all fields for 'extends' have
            # been defined, the extends._fields is used to add these later.
        else:
            fields = dict()
            
        # Create the Element as a subclass of extends.
        self.elements[name]=r=type(name, (extends,), dict(_fields=fields, _subclasses=set(), _abstract=abstract))
        
        # Add the new element to the list of subclasses of its superclass.
        # This allows the superclass to get more fields and add these to this class as well.
        if extends!=AbstractElement:
            extends._subclasses.add(r)
        
        # Return the new Element
        return r
        
    def attribute(self, of, name):
        """Adds an Attribute to an Element."""

        # Disallow starting with an underscore.
        if name[0]=="_":
            raise AttributeError("Attributes can not start with an underscore: {0}".format(name))

        # (Attempt to) add the field.
        self.addfield(of, AttributeField(name=name))
        
    def association(self, parent, child, parentname, childname, limit=None, optional=False):
        """Creates a association between 'parent' and 'child'."""

        # Disallow starting with an underscore
        if parentname[0]=="_":
            raise AttributeError("Association parent names can not start with an underscore: {0}".format(parentname))
        if childname[0]=="_":
            raise AttributeError("Association child names can not start with an underscore: {0}".format(childname))

        # Check duplicate name for self-association
        if id(parent)==id(child) and parentname==childname:
            raise AttributeError("Can't use the same names when defining a self-association: {0}".format(childname))

        # Protect against disallowing the creation of a first element.
        if id(parent)==id(child) and not optional:
            raise AttributeError("Self-associations must be optional: {0} -> {1}".format(childname, parentname))

        # Limit must be positive.
        if limit!=None and not (isinstance(limit, int) and limit>0):
            raise AttributeError("Limit '{2}' must be a positive integer: {0} -> {1}".format(childname, parentname, limit))

        # (Attempt to) add the fields.
        self.addfield(child, ParentField(name=parentname, childname=childname, elementtype=parent, optional=optional))
        self.addfield(parent, ChildListField(name=childname, parentname=parentname, elementtype=child, limit=limit))
    
    def addfield(self, element, fielddescriptor):
        """Verifies that the field does not redefine an old one, 
        adds the field and asks subclasses to do the same."""
        
        # Verify that there are no fields with the same names.
        if fielddescriptor.name in element._fields:
            raise KeyError("Redefinition of field {0}".format(element._fields[fielddescriptor.name].describe()))

        # Disallow the use of python keywords
        if keyword.iskeyword(fielddescriptor.name):
            raise SyntaxError("Python keywords are not allowed: {0}".format(fielddescriptor.name))

        # Add the field
        element._fields[fielddescriptor.name] = fielddescriptor
        
        if hasattr(element, "_subclasses"):
            for subclass in element._subclasses:
                self.addfield(subclass, fielddescriptor)
    
    def instance(self):
        return ModelInstance(self)
        
    def __str__(self):
        """Creates a human readable description of the model."""
        r=["MetaModel object at 0x{0:x}:".format(id(self))]
        for (k,v) in self.elements.items():
            fields = "\n    ".join([w.describe() for w in v._fields.values()])
            if fields:
                fields = "\n    " + fields;
            r.append("Element {0}{1}".format(k, fields))
        return "\n  ".join(r)
        
def load(filename):
    """Loads the MetaModel stored in 'filename'."""
    with open(filename) as f:
        script = compile(f.read(), filename, "exec")
    return MetaModel(script)


class ModelInstance:
    def __init__(self, model):
        """Creates an instance of the metamodel."""
        
        # Create a reference to the model
        self.model = model
        
        # Create a dictionary for storing the named elements of the instance.
        # By convention, the 'graph' will be stored in instance["root"]
        self.identifiers = dict()

    def load(self, filename):
        """Loads the instance of this MetaModel specified by the filename.
        This instance must be new. A reference to 'self' is returned."""
        if filename=="-":
            script = compile(sys.stdin.read(), sys.stdin.name, "exec")
        else:    
            with open(filename) as f:
                script = compile(f.read(), filename, "exec")
        return self.parse(script)

    def parse(self, script):
        # Load the instance
        exec(script, self.model.elements, self.identifiers)
        
        if "root" not in self.identifiers:
            raise KeyError("Instance description does not specify the required 'root' element")
        
        return self
        
    def save(self, filename):
        """Writes this instance to a file."""
        with open(filename, "w") as f:
            print(self, file=f)
    
    def root(self):
        return self.identifiers["root"]
            
    def __serialize_element(self, el):
        """Adds the element to the __repr array. 
        Dependencies are added first."""
        if el in self.__printed:
            return
        self.__printed.add(el)

        args=[]
        children=[]
        # Build the argument list and create a list of children
        for (name,desc) in type(el)._fields.items():
            value = getattr(el, name)
            if isinstance(desc, AttributeField):
                if value != None:
                    args.append("{0}={1}".format(name, repr(value)))
            elif isinstance(desc, ParentField):
                if value!=None:
                    par_el = value
                    self.__serialize_element(par_el)
                    args.append("{0}={1}".format(name, self.__identifiernames[par_el][0]))
            elif isinstance(desc, ChildListField):
                children += value
        
        # Get a string with the identifier(s)
        if el in self.__identifiernames:
            names = " = ".join(self.__identifiernames[el])+" = "
        elif children:
            # Create identifier names for those elements that need it and not yet have one.
            names = "e{0}".format(self.__identifiercounter)
            self.__identifiernames[el] = [names]
            self.__identifiercounter += 1
            names += " = "
        else:
            names = ""
            
        # Add the element to __repr
        self.__repr.append("{0}{1}({2})".format(names, type(el).__name__, ", ".join(args)))
        
        # Descent into the children
        for child in children:
            self.__serialize_element(child)
            
    def __repr__(self):
        """Creates a string which should create the same instance when loaded
        with this instance's meta model."""

        # Make sure that root is set
        if "root" not in self.identifiers:
            raise KeyError("ModelInstance has no root specified")
        
        # Create some temporary fields
        self.__repr = r = []
        self.__printed = set() # used to check whether an element still needs printing
        self.__identifiernames = dict() # contains arrays like ["root"]
        self.__identifiercounter = 0 # used for generating identifiers
        
        # Create identifier names for the elements in self.identifiers.
        for (k,v) in self.identifiers.items():
            if v not in self.__identifiernames:
                self.__identifiernames[v] = []
            self.__identifiernames[v].append(k)
        
        # Add all elements reachable from the 'root' to 'r'
        self.__serialize_element(self.identifiers["root"])
        
        # Remove the temporary fields
        del self.__identifiercounter
        del self.__identifiernames 
        del self.__printed
        del self.__repr
        
        # Return the description
        return "\n".join(r)

# Used by TransformationRule to determine whether to enter the pending rules 
# handling loop, or not.
transforming = False

# This set will contain all rules that have pending transformations.
# It will be empty when the initial transformation call returns.
pending_rules = set()

class TransformationRule:
    """Changes the meaning of a function, such that it can be used to get 
    the result of applying it to an element. It memorizes the result of 
    applying the function to an element, for as long as the element exists.
    It also checks for applying transformation rules in a circular fashion.
    
    The first argument of the decorated function must be an element from
    the source instance (or a tuple of such elements). Additional arguments
    can be passed, however, calling the resulting function multiple times 
    with different arguments is meaningless, as only the first time the 
    arguments are passed to the function.
    
    Also, the decorated function has a 'later' method, that can be 
    used to apply a rule at a later point in time.
    
    TransformationRules work independant of MetaModels and ModelInstances.
    Therefore you can also apply them on non-ModelInstances or create
    non-ModelInstances as a result."""
    
    def __init__(self, f):
        self.f = f
        self.cache = WeakKeyDictionary()
        self.delayed = WeakKeyDictionary()
    
    def __call__(self, element, *args, **kwargs):
        # Are we in the middle of a transformation. If not, set to true and 
        # be the one who applies pending transformations.
        global transforming
        if not transforming:
            # This is the initial call, so we delay it, enter transformation 
            # mode and divert to the pending rules handling loop.
            transforming = True
            self.later(element, *args, **kwargs)
            self.__handle_pending()
            # We are done.
            transforming = False
            # Return the requested element.
            return self.cache[element]
        
        # Check if we have performed the transformation already.
        try:
            r = self.cache[element]
            # Check for circular transformation.
            if r == TransformationRule:
                raise RuntimeError("Applying circular transformation '{0}'".format(self.f.__name__))
            # Return the cached value.
            return r
        except KeyError:
            # Not converted, so do that next.
            pass
        # set the dict value for the current element to 'being transformed'
        self.cache[element] = TransformationRule
        self.cache[element] = r = self.f(element, *args, **kwargs)
        return r
    
    def later(self, element, *args, **kwargs):
        """Will delay the transformation of the specified element, 
        until the transformation returns to the pending rule handling loop."""
        if element in self.cache:
            return
        self.delayed[element] = (args, kwargs)
        pending_rules.add(self)
    
    def __handle_pending(self):
        """Executes the pending rules handling loop."""
        while len(pending_rules)>0:
            # Obtain a pending rule
            rule = pending_rules.pop()
            
            while len(rule.delayed)>0:
                (element, (args, kwargs)) = rule.delayed.popitem()
                rule(element, *args, **kwargs)
    
