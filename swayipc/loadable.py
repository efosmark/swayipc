from abc import ABCMeta
from types import NoneType
from typing import Union, get_type_hints, Any
try:
    from typing import get_args, get_origin
except ImportError:
    get_args = lambda t: getattr(t, '__args__', ())
    get_origin = lambda t: getattr(t, '__origin__', None)

def _value(field_type, value):
        if value is None or value == "none":
            return None
        if issubclass(field_type, Loadable):
            return field_type(value)
        if field_type is Any:
            return value
        return field_type(value)

class Loadable(metaclass=ABCMeta):

    def __new__(cls, data):
        self = super().__new__(cls)
        hints = get_type_hints(cls)
        for key, value in data.items():
            if key not in hints:
                setattr(self, key, value)
                continue
            field_type = hints[key]
            field_origin = get_origin(field_type)
            field_args = set(get_args(field_type))
            if field_origin == list:
                field_type = field_args.pop()
                setattr(self, key, [_value(field_type, v) for v in value])
            elif field_origin == Union and NoneType in field_args and len(field_args) == 2:
                field_args.remove(NoneType)
                field_type = field_args.pop()
                setattr(self, key, _value(field_type, value))
            else:
                setattr(self, key, _value(field_type, value))
        return self

    def __str__(self):
        kv = [
            f"{n}={repr(getattr(self, n))}\n" 
            for n in dir(self)
            if not n.startswith('_') and n not in ['from_dict']
        ]
        return f"{self.__class__.__name__}(\n{', '.join(kv)}\n)"
