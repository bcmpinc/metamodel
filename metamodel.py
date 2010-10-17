#!/usr/bin/python3

class FieldDescriptor:
    """Describes a field of an Element."""
    
    # List of field types.
    ATTRIBUTE = 1
    CHILDLIST = 2
    PARENT    = 3
    
    def __init__(self, type, **kwargs):
        """Creates a descriptor. 
        Parent and child-list arguments come in pairs and need 
        to be able to find each other. Therefore:
        * specify a 'listname' argument when creating a PARENT field;
        * specify a 'name' argument when creating a CHILDLIST field.
        For type checking of PARENT fields, also specify an
        'elementtype' argument. For CHILDLIST fields, the 'elementtype'
        is used for debug output."""
        self.type = type
        if type == FieldDescriptor.PARENT:
            self.listname = kwargs["listname"]
            self.elementtype = kwargs["elementtype"]
        elif type == FieldDescriptor.CHILDLIST:
            self.name = kwargs["name"]
            self.elementtype = kwargs["elementtype"]
    
    def describe(self, name):
        """Used for creating a human readable description of a field."""
        if self.type == FieldDescriptor.ATTRIBUTE:
            return "<attribute> {0}".format(name)
        elif self.type == FieldDescriptor.CHILDLIST:
            return "{0}[] {1}".format(self.elementtype.__name__, name)
        elif self.type == FieldDescriptor.PARENT:
            return "{0} {1}".format(self.elementtype.__name__, name)
        return "<unknown> {1}".format(name)

class AbstractElement(object):
    """The abstract base class used by elements. 
    subclasses need to define self.fields, as a
    dictionary mapping field name to FieldDescriptor."""
    
    def __init__(self, **kwargs):
        """Creates an instance of the element."""
        
        # Create a dictionary for storing the values of the fields.
        self.__dict__["values"] = dict()
        
        # Assign the values specified in the constructor.
        for (k,v) in kwargs.items():
            setattr(self,k,v)
            
        # Verify that all PARENT type attributes are set.
        err = None
        for (k,v) in self.fields.items():
            if v.type == FieldDescriptor.PARENT and k not in self.values:
                if err == None:
                    err = []
                err.append(k)
        # Raise an error if not.
        if err != None:
            raise AttributeError("No parents specified for relation(s) {0}".format(err))
                
        
    def __getattr__(self, name):
        """Returns the requested field of the element.
        If the requested field is a child-list and is not
        yet set, it is initialized with an empty set.
        This set can (but usually should not) be modified."""
        
        # is the value set?, return it.
        if name in self.values:
            return self.values[name]
            
        # if not, check whether it actually is a valid field name.
        if name not in self.fields:
            raise AttributeError("Unknown Attribute '{0}'".format(name))
        
        # If it is a child-list, we need to initialize it first, 
        # as the return value might be modified.
        if self.fields[name].type == FieldDescriptor.CHILDLIST:
            self.values[name] = r = set()
            return r
        
        # Return the default value.
        return None
        
    def __setattr__(self, name, value):
        """Assigns value to the field name. 
        Except when the field is a child-list, because
        it can not be set."""
        
        # Verify that name denotes a valid field name
        if name not in self.fields:
            raise AttributeError("Unknown Attribute '{0}'".format(name))
        
        # Verify that the field is not a childlist
        if self.fields[name].type == FieldDescriptor.CHILDLIST:
            raise AttributeError("Setting value of childlist {0}".format(name))
        
        
        # If a parent field is set, also update the parent's childlist and
        # do type checking.
        field = self.fields[name]
        if field.type == FieldDescriptor.PARENT:
            # Check that value is of the right type and raise a meaning full error otherwise.
            if not isinstance(value, field.elementtype):
                raise AttributeError("Setting {0} to value {1}, which is not an {2}".format(
                    name, value, field.elementtype.__name__))

            # Get a reference to the parent's childlist.
            childlist = getattr(value, field.listname)
                
            # Check of the field was already set
            if name in self.values:
                # Ignore the assignment if it does not change the value
                if id(self.values[name]) == id(value):
                    return

                # Remove the old value
                oldvalue = self.values[name]
                if oldvalue in childlist:
                    childlist.remove(oldvalue)
                    
            # (and) insert the new one.
            childlist.add(value)
            
        # Set the field to the new value.
        self.values[name] = value
    
    def __dir__(self):
        """Returns the field names specified by this Element."""
        return self.fields.keys()
       
       
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
            Relation=self.relation,
        )
        
        # Load the meta-model
        exec(script, modelapi, self.identifiers)
        
        pass

    def metamodel(self):
        """Returns self. Used during the load process."""
        return self
    
    def element(self, of, name):
        """Adds an Element to the meta-model."""
        
        # Verify that the correct value for of is used.
        assert self is of
        
        # Verify that the element name is not yet used.
        if name in self.elements:
            raise KeyError("Redefinition of Element '{0}'".format(name))
        
        # Create the Element as a subclass of AbstractElement.
        self.elements[name]=r=type(name, (AbstractElement,), dict(fields=dict()))
        
        # Return the new Element
        return r
        
    def attribute(self, of, name):
        """Adds an Attribute to an Element."""

        # Verify that there are no fields with the same name.
        if name in of.fields:
            raise KeyError("Redefinition of {1} '{0}'".format(name, of.fields[name].type))

        # Add the field
        of.fields[name] = FieldDescriptor(FieldDescriptor.ATTRIBUTE)
        
    def relation(self, parent, child, name, listname):
        """Creates a relation between 'parent' and 'child'."""

        # Verify that there are no fields with the same names.
        if name in child.fields:
            raise KeyError("Redefinition of {1} '{0}'".format(name, child.fields[name].type))
        if listname in parent.fields:
            raise KeyError("Redefinition of {1} '{0}'".format(listname, parent.fields[listname].type))

        # Add the fields.
        child.fields[name] = FieldDescriptor(FieldDescriptor.PARENT, listname=listname, elementtype=parent)
        parent.fields[listname] = FieldDescriptor(FieldDescriptor.CHILDLIST, name=name, elementtype=child)
        
    def load(self, filename):
        """Loads the instance of this MetaModel specified by 
        the filename."""
        with open(filename) as f:
            script = compile(f.read(), filename, "exec")
        return ModelInstance(self, script) 
        
    def __str__(self):
        r=["MetaModel object at 0x{0:x}:".format(id(self))]
        for (k,v) in self.elements.items():
            fields = "\n    ".join([w.describe(l) for (l,w) in v.fields.items()])
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
    def __init__(self, model, script):
        # Create a reference to the model
        self.model = model
        
        # Create a dictionary for storing the named elements of the instance.
        # By convention, the 'graph' will be stored in instance["root"]
        self.identifiers = dict()

        # Load the instance
        exec(script, model.elements, self.identifiers)
        
        if "root" in self.identifiers:
            self.root = self.identifiers["root"]
        else:
            print("Warning: no 'root' specified.", file=sys.stderr)
            
    def __serialize_element(self, el):
        """Adds the element to the __repr array. 
        Dependencies are added first."""
        if el in self.__printed:
            return self.__printed[el]
        args=[]
        for (name,desc) in type(el).fields:
            if desc.type == FieldDescriptor.ATTRIBUTE:
                args.add("{0}={1}".format(name, getattr(el, desc)))
            elif desc.type == FieldDescriptor.PARENT:
                args.add("{0}={1}".format(name, self.__serialize_element(getattr(el, desc))))
                
            
    def __repr__(self):
        self.__repr = r = []
        self.__printed = dict() # Used to keep track of identifiers.
        self.__identifiercounter = 0
        
        del self.__printed
        del self.__repr
        return "\n".join(r)
        