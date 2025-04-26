import pytest
from typing import Protocol
from strictprotocol import StrictProtocol

# --- Valid Implementation ---

def test_valid_signature_match():
    class P(Protocol):
        def do(self, x: int) -> str: ...

    class Impl(StrictProtocol, P):
        def do(self, x: int) -> str:
            return str(x)

    impl = Impl()
    assert impl.do(42) == "42"

# --- Missing Method ---

def test_missing_method_raises():
    class P(Protocol):
        def do(self) -> None: ...

    with pytest.raises(TypeError, match="missing required method"):
        class Impl(StrictProtocol, P):
            def other(self) -> None:
                pass

# --- Signature Mismatch ---

def test_signature_mismatch_raises():
    class P(Protocol):
        def do(self, x: int) -> str: ...

    with pytest.raises(TypeError, match="Signature mismatch"):
        class Impl(StrictProtocol, P):
            def do(self, x):  # missing return annotation
                return str(x)

# --- Extra Method Allowed ---

def test_extra_methods_allowed():
    class P(Protocol):
        def foo(self) -> int: ...

    class Impl(StrictProtocol, P):
        def foo(self) -> int:
            return 1

        def bar(self):  # extra method
            return "extra"

    assert Impl().foo() == 1
    assert Impl().bar() == "extra"
