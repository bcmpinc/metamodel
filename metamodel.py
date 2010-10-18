
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
        self._values = dict()
        
        # Assign the values specified in the constructor.
        for (k,v) in kwargs.items():
            setattr(self,k,v)
            
        # Verify that all PARENT type attributes are set.
        err = None
        for (k,v) in self._fields.items():
            if v.type == FieldDescriptor.PARENT and k not in self._values:
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
        if name in self._values:
            return self._values[name]
            
        # if not, check whether it actually is a valid field name.
        if name not in self._fields:
            raise AttributeError("Unknown Attribute '{0}'".format(name))
        
        # If it is a child-list, we need to initialize it first, 
        # as the return value might be modified.
        if self._fields[name].type == FieldDescriptor.CHILDLIST:
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
        if self._fields[name].type == FieldDescriptor.CHILDLIST:
            raise AttributeError("Setting value of childlist {0}".format(name))
        
        
        # If a parent field is set, also update the parent's childlist and
        # do type checking.
        field = self._fields[name]
        if field.type == FieldDescriptor.PARENT:
            # Check that value is of the right type and raise a meaning full error otherwise.
            if not isinstance(value, field.elementtype):
                raise AttributeError("Setting {0} to value {1}, which is not an {2}".format(
                    name, value, field.elementtype.__name__))

            # Get a reference to the parent's childlist.
            childlist = getattr(value, field.listname)
                
            # Check of the field was already set
            if name in self._values:
                # Ignore the assignment if it does not change the value
                if id(self._values[name]) == id(self):
                    return

                # Remove the old value
                oldvalue = self._values[name]
                if oldvalue in childlist:
                    childlist.remove(oldvalue)
                    
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
        self.elements[name]=r=type(name, (AbstractElement,), dict(_fields=dict()))
        
        # Return the new Element
        return r
        
    def attribute(self, of, name):
        """Adds an Attribute to an Element."""

        # Verify that there are no fields with the same name.
        if name in of._fields:
            raise KeyError("Redefinition of {1} '{0}'".format(name, of._fields[name].type))

        # Disallow starting with an underscore
        if name[0]=="_":
            raise KeyError("Attributes can not start with an underscore: {0}".format(name))

        # Add the field
        of._fields[name] = FieldDescriptor(FieldDescriptor.ATTRIBUTE)
        
    def relation(self, parent, child, name, listname):
        """Creates a relation between 'parent' and 'child'."""

        # Verify that there are no fields with the same names.
        if name in child._fields:
            raise KeyError("Redefinition of {1} '{0}'".format(name, child._fields[name].type))
        if listname in parent._fields:
            raise KeyError("Redefinition of {1} '{0}'".format(listname, parent._fields[listname].type))
        
        # Disallow starting with an underscore
        if name[0]=="_":
            raise AttributeError("Relation names can not start with an underscore: {0}".format(name))
        if listname[0]=="_":
            raise AttributeError("Relation listnames can not start with an underscore: {0}".format(listname))

        # Add the fields.
        child._fields[name] = FieldDescriptor(FieldDescriptor.PARENT, listname=listname, elementtype=parent)
        parent._fields[listname] = FieldDescriptor(FieldDescriptor.CHILDLIST, name=name, elementtype=child)
        
    def instance(self):
        return ModelInstance(self)
        
    def __str__(self):
        """Creates a human readable description of the model."""
        r=["MetaModel object at 0x{0:x}:".format(id(self))]
        for (k,v) in self.elements.items():
            fields = "\n    ".join([w.describe(l) for (l,w) in v._fields.items()])
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
        with open(filename) as f:
            script = compile(f.read(), filename, "exec")

        # Load the instance
        exec(script, self.model.elements, self.identifiers)
        
        if "root" in self.identifiers:
            self.root = self.identifiers["root"]
        else:
            print("Warning: no 'root' specified.", file=sys.stderr)
        return self
        
    def save(self, filename):
        """Writes this instance to a file."""
        with open(filename, "w") as f:
            print(self, file=f)
            
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
            if desc.type == FieldDescriptor.ATTRIBUTE:
                if value != None:
                    args.append("{0}={1}".format(name, repr(value)))
            elif desc.type == FieldDescriptor.PARENT:
                par_el = value
                self.__serialize_element(par_el)
                args.append("{0}={1}".format(name, self.__identifiernames[par_el][0]))
            elif desc.type == FieldDescriptor.CHILDLIST:
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
        
        # Create some temporary fields
        self.__repr = r = []
        self.__printed = set() # used to check whether an element still needs printing
        self.__identifiernames = dict() # contains arrays like ["root"]
        self.__identifiercounter = 0 # used for generating identifiers
        
        # Create identifier names for the elements in self.identifiers.
        self.identifiers["root"] = self.root # Make sure that root is set
        for (k,v) in self.identifiers.items():
            if v not in self.__identifiernames:
                self.__identifiernames[v] = []
            self.__identifiernames[v].append(k)
        
        # Add all elements reachable from the 'root' to 'r'
        self.__serialize_element(self.root)
        
        # Remove the temporary fields
        del self.__identifiercounter
        del self.__identifiernames 
        del self.__printed
        del self.__repr
        
        # Return the description
        return "\n".join(r)

