import pytest
from parsercraft.codegen_c import CCodeGenerator, CFunction, CVariable, CType
from parsercraft.codegen_wasm import WasmGenerator, WasmModule, WasmFunction, WasmOp, WasmType, WasmImport

class TestCCodeGen:
    def test_c_variable(self):
        v = CVariable(name="x", c_type="int", initial_value="42")
        assert v.declaration() == "int x = 42;"
        
        v2 = CVariable(name="ptr", c_type="char", is_pointer=True, is_const=True)
        assert v2.declaration() == "const char* ptr;"

    def test_c_function(self):
        f = CFunction(
            name="add",
            return_type="int",
            parameters={"a": "int", "b": "int"},
            body=["return a + b;"],
            is_static=True
        )
        sig = f.signature()
        assert "static int add(int a, int b)" in sig or "static int add(int b, int a)" in sig
        
        definition = f.definition()
        assert "return a + b;" in definition
        assert "{" in definition
        assert "}" in definition

    def test_generator_structure(self):
        gen = CCodeGenerator()
        gen.add_include("math.h")
        
        f = CFunction(name="main", return_type="int", body=["return 0;"])
        gen.functions.append(f)
        
        v = CVariable(name="global_var", c_type="int", initial_value="0")
        gen.globals.append(v)
        
        header = gen.generate_header()
        assert '#include "math.h"' in header
        
        # Checking implementations
        # Note: calling generate_implementations()
        impl = gen.generate_implementations()
        assert "int main()" in impl or "int main(void)" in impl or "int main(" in impl


class TestWasmGen:
    def test_wasm_types(self):
        assert WasmType.I32.value == "i32"
        assert WasmType.F64.value == "f64"

    def test_wasm_function_wat(self):
        f = WasmFunction(name="test", params=[("p1", WasmType.I32)], return_type=WasmType.I32)
        # body is list of strings
        f.body.append("i32.const 42")
        
        wat = f.to_wat()
        assert "(func $test" in wat
        assert "(param $p1 i32)" in wat
        assert "(result i32)" in wat
        assert "i32.const 42" in wat

    def test_wasm_module(self):
        m = WasmModule(name="test_mod")
        m.add_import(WasmImport(module="env", name="log", params=[], return_type=None))
        
        f = WasmFunction(name="main")
        m.add_function(f)
        
        wat = m.to_wat()
        assert "(module $test_mod" in wat
        assert '(import "env" "log"' in wat
        
    def test_generator_helpers(self):
        gen = WasmGenerator()
        assert gen.translate_type("int") == WasmType.I32
        assert gen.translate_type("float") == WasmType.F32
