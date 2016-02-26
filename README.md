metamodel
=========
A meta modeling and transformation module for Python 3

The **metamodel** module is used for:

- reading meta model specifications;
- reading instances of that meta model;
- applying a transformation on that meta model.

The **metamodel** module has been created, because it was less work to write
a meta modeling toolkit, than to use the Eclipse Modeling Framework
and the Graphical Modeling Framework. These frameworks are not yet 
production ready and using them requires a lot of debugging and reverse
engineering, because the developers maintain a _zero-documentation_ policy
and any sign of proper design seems to be missing.


Design guidelines
-----------------

So the **metamodel** module is different. It avoids the bad design decisions 
of EMF and GMF. This caused it to follow the following guidelines:

 - Proper documentation. A large set of undocumented examples is insufficient.
 - UML is not perfect. It is still used, but in a slightly modified way.
   Associations are required to have one side with a `1` or `0..1` constraint.
   The other side of the association can not have a lower bound.
   Attributes do not have types or visibilities, only names.
   Classes are named Elements, because `class` is a Python keyword.
 - No XML. XML has a terrible syntax; it is not suited for storing 
   data structures which have elements with multiple parents and XML is
   too often used as an excuse to not specify your input syntax.
 - Be text based. Using only graphical tools for creating meta models and 
   instances can become cumbersome. However, transformations to [graphviz](http://www.graphviz.org/)
   are provided. So you can still make images of your models.
 - No code generation. Custom classes are created during runtime.
 - Keep a small code base.

and the obvious guidelines:

 - Keep it simple stupid.
 - Do only one thing and do it well.
 
 
Use case: Apply transformation
-----------------------------

### Preconditions:
 - There is a meta object factory
 - There are a source and target meta-model (possibly, the source and target meta-model are the same )
 - There is an instance of the source meta-model
 - There are transformation rules from the source meta-model to the target meta-model

### Trigger:
 - Run transformation script

### Guarantee:
 - An instance of the target model is created and stored as a file

### Main Scenario:
 1. The meta object factory module is loaded/imported
   Ex: `import metamodel`
 2. The source and target meta models are loaded
   Ex: `petrinetsmodel = metamodel.load("petrinets.m2")`
 3. The source instance is loaded
   Ex: `petrinet = petrinetsmodel.instance().load("petrinet.m1")`
 4. The transformation rules from source to target meta-model are specified
 5. Transformation rules are applied to the source instance
 6. The created target instance is written to standard output

### Alternatives:
 - There is an error in one of the preconditions
   1. The instance of the target model is not transformed
   2. A description is printed of what went wrong.
   
   
Syntax
------

The syntax used by **metamodel** for meta models and instances is a subset of 
Python. As such it is valid Python code, even though it requires some custom 
functions and classes to be available in the scope in which it is executed.

The syntax of this language in Lazy BNF/EBNF notation is:

    Model = Element+ .
    Element = Identifier "=" Element |
              ElementName "(" FieldList ")" NewLine.
    FieldList = ( Field ("," Field)* )?.
    Field = FieldName "=" Value.
    Value = Identifier | 
            "'" Character* "'" |
            '"' Character* '"' |
            digit+ |
            True |
            False.


Because we use the Python parser, `Identifier`s, `ElementName`s and `FieldName`s 
can not be Python keywords. Every meta model and instance must assign an element to the `root` identifier.
Even though the syntax does not mention it, Python comments are allowed.

The syntax as railroad diagrams: 
(Created with an online [railroad generator](http://www-cgi.uni-regensburg.de/~brf09510/syntax.html).)

### Model
![(model railroad diagram)](https://raw.githubusercontent.com/bcmpinc/metamodel/raw/master/images/syntax_model.png)

### Element
![(element railroad diagram)](https://raw.githubusercontent.com/bcmpinc/metamodel/raw/master/images/syntax_element.png)

### FieldList
![(fieldlist railroad diagram)](https://raw.githubusercontent.com/bcmpinc/metamodel/raw/master/images/syntax_fieldlist.png)

### Field
![(field railroad diagram)](https://raw.githubusercontent.com/bcmpinc/metamodel/raw/master/images/syntax_field.png)

### Value
![(value railroad diagram)](https://raw.githubusercontent.com/bcmpinc/metamodel/raw/master/images/syntax_value.png)


API
---
The most important items provided by the **metamodel** module are:

 - `load(filename)` loads a specification of a meta model. It returns 
   an instance of `MetaModel`.
 - `MetaModel` is a class that contains the description of a model.
   Its `elements` field contains a dictionary of elements defined by the model.
   These elements are subclasses of `AbstractElement`. the `identifiers` field
   contains a dictionary of the identifiers used in the model description. The
   `MetaModel`'s `instance()` method creates an empty instance of this model, which
   is an instance of the class `ModelInstance`.
 - `AbstractElement` is an abstract base class for elements. Subclasses will have 
   their attributes, parents and children available as fields. It has the following 
   private fields for storing meta data:
   - `_fields`, a static field, containing dictionary of `FieldDescriptor`s;
   - `_values`, a dictionary containing the values that are set;
   - `_subclasses`, a static field listing the immediate subclasses;
   - `_abstract`, which is `True` if the class is abstract.
 - `ModelInstance` is a class that contains an instance of a `MetaModel`.
   Instances can be loaded from files using `load(filename)`. Instance descriptions
   can be parsed using `parse(script)`. Its root element can be obtained with `root()`.
   Instances can be written to a file using `save(filename)` and a description can be
   obtained by passing the instance to the global method `repr(object)`.
 - `TransformationRule` is a decorator which should be used for writing down transformations.
   It will cause the transformation function to be applied at most once to each element.
   The transformation is only applied during the first call and will cache the result. 
   Subsequent calls will return the cached result. The decorator also adds a `later(element, ...)`
   method to your function, causing the transformation rule to be applied at a later point in
   time, but before the initial call to a transformation rule terminates. The parameters
   are the same as for the transformation function. The transformation function must take 
   at least one parameter, which is the element that is transformed.
   
   
Known bugs
----------

 - TransformationRule is untested.


Copyright
---------
Copyright &copy; 2010 Bauke Conijn <bcmpinc (at) users.sourceforge.net>
License GPLv3+: [GNU GPL version 3 or (at your option) any later version.](http://gnu.org/licenses/gpl.html)

This  is  free  software:  you  are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
