import pytest
from src.parsercraft.protocols import (
    MethodSignature, PropertyDef, Protocol, StructuralType, 
    ProtocolChecker
)

def test_method_signature_matching():
    # Exact match
    m1 = MethodSignature("foo", "int", [("a", "int")])
    m2 = MethodSignature("foo", "int", [("a", "int")])
    assert m1.signature_matches(m2)
    
    # Return type mismatch
    m3 = MethodSignature("foo", "str", [("a", "int")])
    assert not m1.signature_matches(m3)
    
    # Param type mismatch
    m4 = MethodSignature("foo", "int", [("a", "str")])
    assert not m1.signature_matches(m4)
    
    # Any covariance
    m5 = MethodSignature("foo", "Any", [("a", "int")])
    # match is strict equality or Any
    assert m1.signature_matches(m5) # int != Any, but Any/Any logic
    # Logic in code: if self!=other and self!=Any and other!=Any -> False
    # self=int, other=Any -> passes.
    
    # Param mismatch count
    m6 = MethodSignature("foo", "int", [("a", "int"), ("b", "int")])
    assert not m1.signature_matches(m6)

def test_property_compatibility():
    p1 = PropertyDef("x", "int", is_readonly=True)
    
    # Same name/type/readonly
    p2 = PropertyDef("x", "int", is_readonly=True)
    assert p1.compatible_with(p2)
    
    # Protocol readonly, impl readwrite (is_readonly=False)
    # Code says: if proto.readonly and not impl.readonly -> False
    p3 = PropertyDef("x", "int", is_readonly=False)
    assert not p1.compatible_with(p3) 
    
    # Protocol readwrite, impl readonly
    # Code: if proto.readonly (False) ...
    p_rw = PropertyDef("y", "int", is_readonly=False)
    p_ro = PropertyDef("y", "int", is_readonly=True)
    assert p_rw.compatible_with(p_ro)

def test_protocol_conformance():
    checker = ProtocolChecker()
    
    proto_reader = Protocol(
        "Reader",
        methods={"read": MethodSignature("read", "str", [])}
    )
    
    # Struct implements read
    struct_good = StructuralType(
        methods={"read": MethodSignature("read", "str", [])}
    )
    assert checker.conforms_to_protocol(struct_good, proto_reader)
    
    # Struct missing method
    struct_bad = StructuralType(methods={})
    assert not checker.conforms_to_protocol(struct_bad, proto_reader)
    
    # Struct wrong signature
    struct_wrong = StructuralType(
        methods={"read": MethodSignature("read", "int", [])}
    )
    assert not checker.conforms_to_protocol(struct_wrong, proto_reader)

def test_extract_structural_type():
    checker = ProtocolChecker()
    class_def = {
        "methods": {
            "hello": {"return_type": "void", "parameters": [("name", "str")]}
        },
        "properties": {
            "count": "int"
        }
    }
    
    st = checker.extract_structural_type(class_def)
    assert "hello" in st.methods
    assert st.methods["hello"].return_type == "void"
    assert "count" in st.properties
    assert st.properties["count"].type_ == "int"

def test_find_matching_protocols():
    checker = ProtocolChecker()
    p = Protocol("TestP", methods={"f": MethodSignature("f", "void")})
    checker.register_protocol(p)
    
    st = StructuralType(methods={"f": MethodSignature("f", "void")})
    matches = checker.find_matching_protocols(st)
    assert "TestP" in matches
    
    st2 = StructuralType(methods={})
    matches2 = checker.find_matching_protocols(st2)
    assert "TestP" not in matches2
