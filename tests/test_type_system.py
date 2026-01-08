import pytest
from parsercraft.type_system import Type, TypeKind, TypeSignature, TypeError, TypeEnvironment, AnalysisLevel
from parsercraft.generics import GenericType, TypeParameter, Variance

class TestTypeSystem:
    
    def test_primitive_types(self):
        t_int = Type.int()
        assert t_int.kind == TypeKind.INT
        assert str(t_int) == "int"
        
        t_str = Type.str()
        assert t_str.kind == TypeKind.STR
        
        t_bool = Type.bool()
        assert t_bool.kind == TypeKind.BOOL

    def test_complex_types(self):
        t_list_int = Type.list(Type.int())
        assert t_list_int.kind == TypeKind.LIST
        assert str(t_list_int) == "list[int]"
        
        t_dict = Type.dict(Type.str(), Type.int())
        assert t_dict.kind == TypeKind.DICT
        assert str(t_dict) == "dict[str, int]"

    def test_compatibility(self):
        t_int = Type.int()
        t_int2 = Type.int()
        t_str = Type.str()
        
        assert t_int.is_compatible_with(t_int2)
        assert not t_int.is_compatible_with(t_str)
        
        t_opt_int = Type.optional(Type.int())
        # Optional[int] compatible with int? usually int compatible with optional, but checks logic
        # Implementation says: if self.kind == TypeKind.OPTIONAL: return self.type_args[0].is_compatible_with(other)
        
        # Test case: Is Optional[Int] compatible with Int?
        # Logic in Type.is_compatible_with:
        # if self.kind == TypeKind.OPTIONAL: return self.type_args[0].is_compatible_with(other)
        # So Optional[Int].is_compatible_with(Int) -> Int.is_compatible_with(Int) -> True
        assert t_opt_int.is_compatible_with(t_int)
        
    def test_type_environment(self):
        env = TypeEnvironment()
        t_int = Type.int()
        env.define_variable("x", t_int)
        
        assert env.get_variable_type("x") == t_int
        assert env.get_variable_type("y") is None
        
        # Nested environment
        child = TypeEnvironment(parent=env)
        assert child.get_variable_type("x") == t_int
        
        t_str = Type.str()
        child.define_variable("y", t_str)
        assert child.get_variable_type("y") == t_str
        assert env.get_variable_type("y") is None


class TestGenerics:
    
    def test_type_parameter(self):
        tp = TypeParameter("T")
        assert tp.name == "T"
        assert str(tp) == "T"
        
        tp_bounded = TypeParameter("N", constraint="Number")
        assert str(tp_bounded) == "N extends Number"

    def test_generic_type(self):
        T = TypeParameter("T")
        gen_list = GenericType("List", parameters=[T])
        
        assert gen_list.is_generic()
        assert str(gen_list) == "List[T]"
        
    def test_generic_binding(self):
        T = TypeParameter("T")
        gen_list = GenericType("List", parameters=[T])
        
        bound_list = gen_list.bind({"T": "int"})
        assert not bound_list.is_generic()
        assert str(bound_list) == "List[int]"
        
        # Test default
        U = TypeParameter("U", default="str")
        gen_map = GenericType("Map", parameters=[U])
        bound_map = gen_map.bind({})
        assert str(bound_map) == "Map[str]"
