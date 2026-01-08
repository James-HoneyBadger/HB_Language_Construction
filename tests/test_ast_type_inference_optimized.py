import pytest
from src.parsercraft.ast_integration import ASTNode
from src.parsercraft.ast_type_inference_optimized import OptimizedTypeInferencePass

class MockInferencePass(OptimizedTypeInferencePass):
    def __init__(self):
        super().__init__()
        self.visited_count = 0
    
    def visit_test_node(self, node):
        self.visited_count += 1
        return "int"

def test_inference_caching():
    pass_ = MockInferencePass()
    node = ASTNode(node_type="test_node")
    
    # First visit
    result1 = pass_.visit(node)
    assert result1 == "int"
    assert pass_.visited_count == 1
    
    # Second visit - should return from cache, not increment visited_count
    result2 = pass_.visit(node)
    assert result2 == "int"
    assert pass_.visited_count == 1
    
    # New node check
    node2 = ASTNode(node_type="test_node")
    result3 = pass_.visit(node2)
    assert result3 == "int"
    assert pass_.visited_count == 2

def test_compatibility_cache():
    pass_ = OptimizedTypeInferencePass()
    
    # "int" vs "float" -> True (coercion)
    assert pass_._check_type_compatibility("int", "float")
    
    # Cache manual check
    key = ("int", "float")
    assert key in pass_._type_compat_matrix
    assert pass_._type_compat_matrix[key] == True
    
    # "int" vs "string" -> False
    assert not pass_._check_type_compatibility("int", "string")

def test_compatibility_logic():
    pass_ = OptimizedTypeInferencePass()
    assert pass_._is_compatible("int", "int")
    assert pass_._is_compatible("int", "float")
    assert pass_._is_compatible("float", "int")
    assert pass_._is_compatible("any", "string")
    assert pass_._is_compatible("string", "any")
    assert not pass_._is_compatible("int", "string")

def test_clear_cache():
    pass_ = MockInferencePass()
    node = ASTNode(node_type="test_node")
    pass_.visit(node)
    
    pass_._check_type_compatibility("int", "float")
    
    stats = pass_.get_cache_stats()
    assert stats["nodes_cached"] == 1
    assert stats["type_compat_cached"] == 1
    
    pass_.clear_cache()
    stats = pass_.get_cache_stats()
    assert stats["nodes_cached"] == 0
    assert stats["type_compat_cached"] == 0
