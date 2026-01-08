import pytest
from types import SimpleNamespace
from parsercraft.generics import (
    GenericType,
    TypeParameter,
    Variance,
    GenericFunction,
    GenericClass,
    GenericChecker
)
from parsercraft.type_system_generics import GenericsTypeChecker

class TestGenericsCore:
    def test_type_parameter(self):
        t = TypeParameter("T", constraint="Number")
        assert t.name == "T"
        assert t.constraint == "Number"
        assert str(t) == "T extends Number"

    def test_generic_type_binding(self):
        t = TypeParameter("T")
        generic_list = GenericType("List", [t])
        
        bound_list = generic_list.bind({"T": "int"})
        assert bound_list.arguments == ["int"]
        assert not bound_list.is_generic()

    def test_generic_function_instantiation(self):
        t = TypeParameter("T")
        func = GenericFunction(
            name="identity",
            type_parameters=[t],
            parameter_types={"x": "T"},
            return_type="T"
        )
        
        concrete = func.instantiate({"T": "int"})
        assert concrete.parameter_types["x"] == "int"
        assert concrete.return_type == "int"

    def test_generic_class_instantiation(self):
        t = TypeParameter("T")
        cls = GenericClass(
            name="Container",
            type_parameters=[t],
            fields={"value": "T"}
        )
        
        concrete = cls.instantiate({"T": "str"})
        assert concrete.fields["value"] == "str"

class TestGenericChecker:
    def setup_method(self):
        self.checker = GenericChecker()

    def test_constraint_checking(self):
        t = TypeParameter("T", constraint="Number")
        assert self.checker.check_constraint(t, "int")
        assert self.checker.check_constraint(t, "float")
        assert not self.checker.check_constraint(t, "str")

    def test_generic_assignment_invariant(self):
        t = TypeParameter("T", variance=Variance.INVARIANT)
        # Using fix in generics.py (explicitly checking mismatch)
        
        l1 = GenericType("List", [t], ["int"])
        l2 = GenericType("List", [t], ["int"])
        l3 = GenericType("List", [t], ["float"])
        
        assert self.checker.check_generic_assignment(l1, l2)
        assert not self.checker.check_generic_assignment(l1, l3)

    def test_generic_assignment_covariant(self):
        t = TypeParameter("T", variance=Variance.COVARIANT)
        l_any = GenericType("List", [t], ["Any"])
        l_int = GenericType("List", [t], ["int"])
        
        assert self.checker.check_generic_assignment(l_any, l_int)

    def test_argument_inference(self):
        t = TypeParameter("T")
        func = GenericFunction(
            name="identity",
            type_parameters=[t],
            parameter_types={"x": "T"},
            return_type="T"
        )
        
        inferred = self.checker.infer_type_arguments(func, {"x": "int"})
        assert inferred == {"T": "int"}
        
        func2 = GenericFunction(
            name="pair",
            type_parameters=[t],
            parameter_types={"x": "T", "y": "T"},
            return_type="T"
        )
        inferred_conflict = self.checker.infer_type_arguments(func2, {"x": "int", "y": "str"})
        assert inferred_conflict is None

class TestGenericsTypeChecker:
    def setup_method(self):
        self.mock_config = SimpleNamespace(
            built_in_functions=[],
            primitive_types=["int", "str", "bool", "float", "void", "Any"],
            any_type="Any"
        )

    def test_check_generic_function(self):
        checker = GenericsTypeChecker(config=self.mock_config)
        errors = checker.check_generic_function("map", ["T", "U"], {})
        assert not errors
        assert "map" in checker.generic_functions
        
    def test_check_generic_class(self):
        checker = GenericsTypeChecker(config=self.mock_config)
        errors = checker.check_generic_class("Box", ["T"], {})
        assert not errors
        assert "Box" in checker.generic_classes
        
    def test_instantiation_check(self):
        checker = GenericsTypeChecker(config=self.mock_config)
        checker.check_generic_class("Box", ["T"], {})
        
        success, errors = checker.check_generic_instantiation("Box", ["int"])
        assert success
        
        success, errors = checker.check_generic_instantiation("Box", ["int", "str"])
        assert not success
