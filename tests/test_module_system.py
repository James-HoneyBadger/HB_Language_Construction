import pytest
from pathlib import Path
from unittest.mock import MagicMock
from parsercraft.module_system import (
    ModuleLoader, Module, ModuleImport, ModuleExport, ModuleVisibility, ModuleMetadata
)

class TestModuleSystem:
    
    def test_module_import_basics(self):
        imp = ModuleImport(module_name="math", alias="m")
        assert imp.get_reference_name() == "m"
        
        imp2 = ModuleImport(module_name="math")
        assert imp2.get_reference_name() == "math"

    def test_module_export_accessibility(self):
        m1 = Module(name="mod1", path=Path("mod1.lang"), content="", language_config=None)
        m2 = Module(name="mod2", path=Path("mod2.lang"), content="", language_config=None)
        
        # Public export
        exp = ModuleExport(name="foo", kind="function", visibility=ModuleVisibility.PUBLIC)
        assert exp.is_accessible_from(m2)
        
        # Private export (defined at None by default, let's say defined in m1)
        exp_priv = ModuleExport(
            name="secret", 
            kind="variable", 
            visibility=ModuleVisibility.PRIVATE, 
            defined_at="mod1"
        )
        assert exp_priv.is_accessible_from(m1) # Same module
        assert not exp_priv.is_accessible_from(m2) # Different module

    def test_parse_simple_import(self):
        loader = ModuleLoader(config=None)
        
        # Test "import math"
        imp = loader._parse_import_statement("import math")
        assert imp.module_name == "math"
        assert imp.alias is None
        
        # Test "import math as m"
        imp = loader._parse_import_statement("import math as m")
        assert imp.module_name == "math"
        assert imp.alias == "m"
        
        # Test "import math version '1.0'"
        imp = loader._parse_import_statement("import math version '1.0'")
        assert imp.version_constraint == "1.0"

    def test_parse_destructuring_import(self):
        loader = ModuleLoader(config=None)
        imp = loader._parse_import_statement("import {sin, cos} from math")
        assert imp.module_name == "math"
        assert "sin" in imp.selected
        assert "cos" in imp.selected

    def test_parse_export(self):
        loader = ModuleLoader(config=None)
        
        # Function export
        exp = loader._parse_export_statement("export function myFunc(a, b)", 10)
        assert exp.name == "myFunc"
        assert exp.kind == "function"
        
        # Const export
        exp = loader._parse_export_statement("export const PI = 3.14", 20)
        assert exp.name == "PI"
        assert exp.kind == "variable"
        # Name might extraction logic check needed
        
        # Class export
        exp = loader._parse_export_statement("export class MyClass", 30)
        assert exp.name == "MyClass"
        assert exp.kind == "class"

    def test_module_loader_integration(self, tmp_path):
        # Create a real file
        p = tmp_path / "testmod.lang"
        p.write_text("""
import math as m
export function hello()
export const VAL = 42
""")
        
        loader = ModuleLoader(config=None)
        module = loader.load_file(p)
        
        assert module.name == "testmod"
        assert len(module.dependencies) == 1
        assert module.dependencies[0].alias == "m"
        
        assert len(module.exports) == 2
        # Verify keys in exports dict
        assert "hello" in module.exports
        assert "VAL" in module.exports
        
    def test_module_metadata(self, tmp_path):
        p = tmp_path / "module.json"
        p.write_text('{"name": "testpkg", "version": "1.2.3"}')
        
        meta = ModuleMetadata.from_file(p)
        assert meta.name == "testpkg"
        assert meta.version == "1.2.3"
