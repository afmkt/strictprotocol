import inspect
from typing import Protocol, get_type_hints, _ProtocolMeta
from types import FunctionType, MethodType

def get_callable_members(cls):
    return {
        name: value
        for name, value in cls.__dict__.items()
        if isinstance(value, (FunctionType, MethodType))
    }

def unwrap_method(func):
    while hasattr(func, "__wrapped__"):
        func = func.__wrapped__
    return func

def is_signature_compatible(proto_func, impl_func):
    proto_sig = inspect.signature(proto_func)
    impl_sig = inspect.signature(impl_func)
    return proto_sig == impl_sig

class StrictProtocolMeta(_ProtocolMeta):
    def __init__(cls, name, bases, namespace, **kwargs):
        proto_bases = [b for b in bases if isinstance(b, type) and issubclass(b, Protocol)]
        if not proto_bases:
            return

        for proto_base in proto_bases:
            proto_methods = get_callable_members(proto_base)
            impl_methods = get_callable_members(cls)

            for method_name, proto_method in proto_methods.items():
                if method_name == "__init__":  # Skip __init__
                    continue                
                if method_name not in impl_methods:
                    raise TypeError(f"{cls.__name__} is missing required method: `{method_name}`")

                proto_func = unwrap_method(proto_method)
                impl_func = unwrap_method(impl_methods[method_name])

                if not is_signature_compatible(proto_func, impl_func):
                    raise TypeError(
                        f"Signature mismatch in `{cls.__name__}.{method_name}`:\n"
                        f"  Expected: {inspect.signature(proto_func)} with {get_type_hints(proto_func)}\n"
                        f"  Found:    {inspect.signature(impl_func)} with {get_type_hints(impl_func)}"
                    )

        super().__init__(name, bases, namespace)

class StrictProtocol(metaclass=StrictProtocolMeta):
    pass
