import pytest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
from parsercraft.language_runtime import LanguageRuntime
from parsercraft.language_config import LanguageConfig, KeywordMapping, FunctionConfig, SyntaxOptions

class TestLanguageRuntime:
    def setup_method(self):
        LanguageRuntime.reset()
    
    def teardown_method(self):
        LanguageRuntime.reset()

    def test_singleton(self):
        r1 = LanguageRuntime.get_instance()
        r2 = LanguageRuntime.get_instance()
        assert r1 is r2
        
        r3 = LanguageRuntime()
        assert r1 is r3

    def test_load_config_object(self):
        config = MagicMock(spec=LanguageConfig)
        config.name = "TestConfig"
        config.syntax_options = MagicMock()
        config.keyword_mappings = {}
        config.builtin_functions = {}
        
        LanguageRuntime.load_config(config=config)
        assert LanguageRuntime.get_config() is config

    def test_translate_keyword(self):
        # Setup mock config
        config = MagicMock(spec=LanguageConfig)
        config.name = "TestConfig"
        
        # Mappings: 'si' -> 'if'
        kw_map = KeywordMapping(original="if", custom="si")
        config.keyword_mappings = {"if": kw_map}
        
        # Stub syntax options
        config.syntax_options = MagicMock()
        config.syntax_options.enable_satirical_keywords = False
        config.builtin_functions = {}

        LanguageRuntime.load_config(config=config)
        
        assert LanguageRuntime.translate_keyword("si") == "if"
        assert LanguageRuntime.translate_keyword("unknown") == "unknown"
        
    def test_translate_function(self):
        config = MagicMock(spec=LanguageConfig)
        config.name = "TestConfig"
        config.keyword_mappings = {}
        
        # Function: 'imprimir' -> 'print'
        # implementation defaults to None, so name is used unless specified
        func_def = FunctionConfig(name="imprimir", arity=1, implementation="print", enabled=True)
        config.builtin_functions = {"imprimir": func_def}
        
        config.syntax_options = MagicMock(enable_satirical_keywords=False)
        
        LanguageRuntime.load_config(config=config)
        
        assert LanguageRuntime.translate_function("imprimir") == "print" 
        # Wait, build_mappings puts func.name -> impl in map.
        # implementation defaults to name if None.
        
        # Let's verify the logic in LanguageRuntime._build_mappings:
        # impl = func.implementation or func.name
        # self._function_map[func.name] = impl
        
        # If I want translation I should check what is put in map.
        # If custom is keys, then we are looking up by custom name.
        # Here 'imprimir' is the Key in builtin_functions dict probably?
        # Actually builtin_functions is Dict[str, FunctionDefinition].
        # FunctionDefinition has 'name' field which usually matches the key.
        
        # Let's retry with more explicit setup
        pass

    def test_translate_function_logic(self):
        # Create a real config to avoid mock complexity
        config = LanguageConfig()
        # Add a custom function
        f = FunctionConfig(name="imprimir", arity=1, implementation="print", enabled=True)
        config.builtin_functions["imprimir"] = f
        
        LanguageRuntime.load_config(config=config)
        
        # Logic: func.name ('imprimir') -> impl ('print')
        assert LanguageRuntime.translate_function("imprimir") == "print"
        
    def test_syntax_options(self):
        config = LanguageConfig()
        config.syntax_options.array_start_index = 1
        config.syntax_options.allow_fractional_indexing = True
        
        LanguageRuntime.load_config(config=config)
        
        assert LanguageRuntime.get_array_start_index() == 1
        assert LanguageRuntime.is_fractional_indexing_enabled() is True
        
    def test_is_keyword_enabled(self):
        config = LanguageConfig()
        # Default config has mappings. Let's clear them and add one.
        config.keyword_mappings = {
            "if": KeywordMapping(original="if", custom="si")
        }
        
        LanguageRuntime.load_config(config=config)
        
        assert LanguageRuntime.is_keyword_enabled("if")
        assert not LanguageRuntime.is_keyword_enabled("while")

    @patch('parsercraft.language_config.LanguageConfig.load')
    def test_load_config_file(self, mock_load):
        mock_config = MagicMock(spec=LanguageConfig)
        mock_config.name = "FileConfig"
        mock_config.syntax_options = MagicMock(enable_satirical_keywords=False)
        mock_config.keyword_mappings = {}
        mock_config.builtin_functions = {}
        
        mock_load.return_value = mock_config
        
        LanguageRuntime.load_config(config_file="test.yaml")
        
        mock_load.assert_called_once_with("test.yaml")
        assert LanguageRuntime.get_config() is mock_config

