import pytest
from types import SimpleNamespace
from parsercraft.type_system import Type, TypeKind
from parsercraft.protocols import Protocol, MethodSignature
from parsercraft.protocol_type_integration import (
    ProtocolTypeIntegration,
    TypeCompatibilityResult
)
from parsercraft.protocol_type_optimized import OptimizedProtocolTypeIntegration

class MockTypeChecker:
    def __init__(self, config=None):
        self.config = config

class TestProtocolTypeIntegration:
    def setup_method(self):
        self.type_checker = MockTypeChecker()
        self.integration = ProtocolTypeIntegration(self.type_checker)
        
        # Define a standard Reader protocol
        self.reader_protocol = Protocol(
            name="Reader",
            methods={
                "read": MethodSignature("read", "str", [], is_optional=False)
            }
        )
        self.integration.register_protocol(self.reader_protocol)

    def test_register_protocol(self):
        p = Protocol("Writer", methods={})
        self.integration.register_protocol(p)
        assert "Writer" in self.integration.protocols

    def test_check_protocol_conformance_success(self):
        from parsercraft.protocols import StructuralType
        
        struct_type = StructuralType(
            methods={"read": MethodSignature("read", "str", [], False)}
        )
        
        # FIX: Type constructor is (kind, name)
        type_obj = Type(TypeKind.CLASS, "MyReader")
        
        # Inject into cache
        self.integration.structural_types["MyReader"] = struct_type
        
        result = self.integration.check_protocol_conformance(type_obj, self.reader_protocol)
        assert result.compatible
        assert "conforms to protocol Reader" in result.reason

    def test_check_protocol_conformance_failure(self):
        from parsercraft.protocols import StructuralType
        
        # Missing 'read' method
        struct_type = StructuralType(methods={})
        type_obj = Type(TypeKind.CLASS, "NotAReader")
        
        self.integration.structural_types["NotAReader"] = struct_type
        
        result = self.integration.check_protocol_conformance(type_obj, self.reader_protocol)
        assert not result.compatible
        assert "method read" in result.missing_features[0]

    def test_check_type_compatibility_target_protocol(self):
        from parsercraft.protocols import StructuralType
        
        struct_type = StructuralType(
            methods={"read": MethodSignature("read", "str", [], False)}
        )
        source = Type(TypeKind.CLASS, "MyReader")
        # FIX: Use TypeKind.CLASS (or generic) for protocol type placeholder
        target = Type(TypeKind.CLASS, "Reader") 
        
        self.integration.structural_types["MyReader"] = struct_type
        
        result = self.integration.check_type_compatibility(
            source, target, check_protocols=True
        )
        assert result.compatible

class TestOptimizedProtocolIntegration:
    def setup_method(self):
        self.type_checker = MockTypeChecker()
        self.integration = OptimizedProtocolTypeIntegration(self.type_checker)
        
        self.reader_protocol = Protocol(
            name="Reader",
            methods={
                "read": MethodSignature("read", "str", [], is_optional=False)
            }
        )
        self.integration.register_protocol(self.reader_protocol)

    def test_caching_behavior(self):
        from parsercraft.protocols import StructuralType
        
        struct_type = StructuralType(
            methods={"read": MethodSignature("read", "str", [], False)}
        )
        source = Type(TypeKind.CLASS, "MyReader")
        target = Type(TypeKind.CLASS, "Reader")
        
        self.integration.structural_types["MyReader"] = struct_type
        
        # First check - manual (using check_protocols=True, implicitly checking if target is protocol)
        # Note: Optimized overload signature mismatch?
        # Optimized class: def check_type_compatibility(self, source_type: Type, target_type: Type, is_protocol: bool, context: Optional[Dict] = None)
        # Base class: def check_type_compatibility(self, source_type: Type, target_type: Type, check_protocols: bool = True, environment: Optional[TypeEnvironment] = None)
        
        # Wait, looking at protocol_type_optimized.py:
        # check_type_compatibility(self, source_type: Type, target_type: Type, is_protocol: bool, context: Optional[Dict] = None)
        # It changes argument names? 'is_protocol' vs 'check_protocols'. 'context' vs 'environment'.
        
        result1 = self.integration.check_type_compatibility(
            source, target, is_protocol=True
        )
        assert result1.compatible
        
        # Verify it's in cache
        cache_key = ("MyReader", "Reader")
        assert cache_key in self.integration._conformance_cache
        assert self.integration._conformance_cache[cache_key] is True
        
        # Second check - from cache
        result2 = self.integration.check_type_compatibility(
            source, target, is_protocol=True
        )
        assert result2.compatible

    def test_method_hashing(self):
        hashes = self.integration._protocol_method_cache.get("Reader")
        assert hashes is not None
        assert len(hashes) == 1
        # access the only element
        h = list(hashes)[0]
        assert h.name == "read"
        assert h.return_type == "str"
