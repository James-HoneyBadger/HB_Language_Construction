import pytest
import json
import pickle
from parsercraft.interpreter_generator import InterpreterPackage
from parsercraft.language_config import LanguageConfig
from parsercraft.language_runtime import LanguageRuntime

class TestInterpreterGenerator:
    def setup_method(self):
        LanguageRuntime.reset()
        
    def test_init(self):
        config = LanguageConfig(name="TestLang")
        pkg = InterpreterPackage(config)
        
        assert pkg.name == "TestLang"
        assert pkg.metadata["name"] == "TestLang"
        # Since config is empty, default keywords are loaded
        # LanguageConfig defaults has many keywords
        assert pkg.metadata["keywords"] > 0
        
    def test_serialization(self):
        config = LanguageConfig(name="SerTest")
        pkg = InterpreterPackage(config)
        
        # To Dict
        d = pkg.to_dict()
        assert d["metadata"]["name"] == "SerTest"
        assert d["config"]["metadata"]["name"] == "SerTest"
        
        # To JSON
        j = pkg.to_json()
        assert "SerTest" in j
        
        # To Pickle
        p = pkg.to_pickle()
        assert isinstance(p, bytes)
        
        # From Dict
        pkg2 = InterpreterPackage.from_dict(d)
        assert pkg2.name == "SerTest"
        assert pkg2.config.name == "SerTest"

    def test_execute_fallback(self):
        config = LanguageConfig(name="ExecTest")
        pkg = InterpreterPackage(config)
        
        # Expect fallback execution (LanguageRuntime has no execute)
        res = pkg.execute("print('hello')")
        
        assert res["status"] == "success"
        assert res["output"] == {}

    def test_execute_with_mock_runtime(self):
        config = LanguageConfig(name="MockExec")
        pkg = InterpreterPackage(config)
        
        # Mock execute on runtime
        mock_exec = lambda code: f"Executed: {code}"
        pkg.runtime.execute = mock_exec
        pkg.runtime.globals = {"x": 10}
        
        res = pkg.execute("some code")
        
        assert res["status"] == "success"
        assert res["output"] == "Executed: some code"
        assert res["variables"] == {"x": 10}
