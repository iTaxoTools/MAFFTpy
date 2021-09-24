# -----------------------------------------------------------------------------
# Param - Parameter primitives
# Copyright (C) 2021  Patmanidis Stefanos
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------


"""
Parameter primitives to hold values and metadata.
First define the model as a root Group with children.
Then access the Field values using Group attributes.

Usage example:

    from itaxotools.common.param import Field, Group

    param = Group(
        key='root',
        label='General',
        children=[
            Field('alpha', default='lorem'),
            Field('beta', value=42, doc='The answer'),
            Group(
                key='general',
                children=[
                    Field('gamma', list=[1, 2, 3], value=2),
                    Field('delta', type=int, value=1),
                    Field('epsilon', range=(1, 10), value=1),
                ])
        ])

    param.alpha = 'ipsum'
    print(param.beta.doc, param.beta.value)
    if param.beta == 42:
        print('This is True')
    try:
        param.general.gamma = 5
    except ValueError as e:
        print('Exception:', str(e))
    try:
        param.general.delta = '5'
    except TypeError as e:
        print('Exception:', str(e))
    data = param.dumps()
    data['general']['epsilon'] = 10
    param.loads(data)
    print(repr(param.general))

"""


class Field():
    """
    Contains the Field value and other metadata.
    New values are cheked against type, list and range (if defined).
    Using comparison operators on the Field compare against its value.
    """

    def __init__(self, key, **kwargs):
        """
        The key must be a valid Python variable name.
        All keyword arguments become attributes.
        """
        self.key = None
        self.label = None
        self.doc = None
        self.default = None
        self.list = {}
        self.range = (None, None)
        self._value = None
        self._parent = None
        self._type = type(None)

        if isinstance(key, str) and key.isidentifier():
            self.key = key
        else:
            raise TypeError(
                f'key {repr(key)} is not a valid string identifier')

        # Assign these in order
        if 'type' in kwargs:
            self.type = kwargs.pop('type')
        if 'list' in kwargs:
            self.list = kwargs.pop('list')
        if 'range' in kwargs:
            self.range = kwargs.pop('range')
        if 'default' in kwargs:
            self.default = kwargs.pop('default')
            self.value = self.default
        if 'value' in kwargs:
            self.value = kwargs.pop('value')

        for attr in kwargs:
            setattr(self, attr, kwargs[attr])

    def __str__(self):
        label = self.label if self.label is not None else self.key
        return (f'{self.__class__.__name__}(\'{label}\': {self.value})')

    def __repr__(self):
        parent = None if self._parent is None else (
            f'{self._parent.__class__.__name__}'
            f'({repr(self._parent.key)} at {hex(id(self._parent))})'
            )
        return (
            f'{self.__class__.__name__}('
            f'key={repr(self.key)}, '
            f'value={repr(self.value)}, '
            f'type={repr(self.type)}, '
            f'label={repr(self.label)}, '
            f'doc={repr(self.doc)}, '
            f'default={repr(self.default)}, '
            f'list={repr(self.list)}, '
            f'range={repr(self.range)}, '
            f'parent={parent}'
            f') at {hex(id(self))}'
            )

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __lt__(self, other):
        return self.value < other

    def __gt__(self, other):
        return self.value > other

    def __le__(self, other):
        return self.value <= other

    def __ge__(self, other):
        return self.value >= other

    def _get_type(self):
        return self._type

    def _set_type(self, x):
        if not isinstance(x, type):
            raise TypeError(f'new type {x} is not a type')
        self._type = x

    def _get_value(self):
        return self._value

    def _set_value(self, x):
        """Check new value against type, range and list"""
        if not issubclass(self.type, type(None)):
            if not isinstance(x, self.type):
                raise TypeError((
                    f'new value {repr(x)} '
                    f'for field {repr(self.key)} '
                    f'not of type {self.type.__name__}'))
        if self.list and x not in self.list:
            raise ValueError((
                f'new value {repr(x)} '
                f'for field {repr(self.key)} '
                f'not in list'))
        if self.range[0] is not None and x < self.range[0]:
            raise ValueError((
                f'new value {repr(x)} '
                f'for field {repr(self.key)} '
                f'is less than {self.range[0]}'))
        if self.range[1] is not None and x > self.range[1]:
            raise ValueError((
                f'new value {repr(x)} '
                f'for field {repr(self.key)} '
                f'is more than {self.range[1]}'))
        self._value = x

    type = property(_get_type, _set_type)
    value = property(_get_value, _set_value)


class Group(object):
    """
    Contains the Group children and other metadata.
    Access the children either by key or attribute.
    Assignment operator on a Field child sets its value.
    Children are added in order.
    """

    def __init__(self, key, **kwargs):
        """
        The key must be a valid Python variable name.
        All keyword arguments become attributes.
        If a children list is provided, they are properly added.
        """
        self.key = None
        self.label = None
        self.doc = None
        self._children = {}
        self._parent = None

        if isinstance(key, str) and key.isidentifier():
            self.key = key
        else:
            raise TypeError(
                f'key {repr(key)} is not a valid string identifier')

        if 'children' in kwargs:
            for child in kwargs['children']:
                self.add(child)
            kwargs.pop('children')

        for attr in kwargs:
            setattr(self, attr, kwargs[attr])

    def __str__(self):
        label = self.label if self.label is not None else self.key
        return (
            f'{self.__class__.__name__}(\'{label}\': '
            f'{list(self._children.keys())})')

    def __repr__(self):
        children = ', '.join([(
            f'{self._children[x].__class__.__name__}'
            f'({repr(x)} at {hex(id(self._children[x]))})'
            ) for x in self._children])
        parent = None if self._parent is None else (
            f'{self._parent.__class__.__name__}'
            f'({repr(self._parent.key)} at {hex(id(self._parent))})'
            )
        return (
            f'{self.__class__.__name__}('
            f'key={repr(self.key)}, '
            f'label={repr(self.label)}, '
            f'doc={repr(self.doc)}, '
            f'children=[{children}], '
            f'parent={parent}'
            f') at {hex(id(self))}'
            )

    def __getitem__(self, child):
        return self._children[child]

    def __delitem__(self, child):
        self._children[child]._parent = None
        del self._children[child]

    def __setitem__(self, key, x):
        if key in self._children and isinstance(self._children[key], Field):
            self._children[key].value = x
        else:
            raise TypeError(f'Group {repr(self.key)} has no Field \'{key}\'')

    def __getattr__(self, attr):
        try:
            super().__getattribute__('_children')
        except AttributeError:
            return super().__getattribute__(attr)
        else:
            if attr in self._children:
                return self[attr]
            else:
                raise AttributeError(
                    f'Group has no attribute or child {repr(attr)}')

    def __setattr__(self, attr, x):
        if hasattr(self, '_children') and attr in self._children:
            self[attr] = x
        else:
            super().__setattr__(attr, x)

    def __delattr__(self, attr):
        if hasattr(self, '_children') and attr in self._children:
            del self[attr]
        else:
            super().__delattr__(attr)

    def __dir__(self):
        return super().__dir__() + list(self._children.keys())

    def add(self, x):
        """Add a Field or Group while properly setting key and parent"""
        if not ((isinstance(x, Field) or isinstance(x, Group))):
            raise TypeError(f'new child {x} is not a Field or Group')
        if x.key in super().__dir__():
            raise ValueError(
                f'new child key {repr(x.key)} conflicts with Group dir')
        self._children[x.key] = x
        x._parent = self

    def dumps(self):
        """Export all values as a nested dictionary"""
        d = dict()
        for key, child in self._children.items():
            if isinstance(child, Field):
                d[key] = child.value
            elif isinstance(child, Group):
                d[key] = child.dumps()
            else:
                raise TypeError(
                    f'unexpected child {repr(child)} of type {type(child)}')
        return d

    def loads(self, data):
        """Import values from a nested dictionary"""
        for key, value in data.items():
            if isinstance(self._children[key], Field):
                self[key] = value
            elif isinstance(self._children[key], Group):
                self[key].loads(value)
            else:
                raise KeyError(f'no child for key {repr(key)}')
