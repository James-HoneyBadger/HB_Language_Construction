import pytest
from parsercraft.language_config import LanguageConfig

class TestPresets:
    def test_functional_preset(self):
        config = LanguageConfig.from_preset("functional")
        assert config.name == "Functional Lambda"
        assert config.keyword_mappings["def"].custom == "define"
        assert config.keyword_mappings["lambda"].custom == "lambda"
        
    def test_lisp_like_preset(self):
        config = LanguageConfig.from_preset("lisp_like")
        assert config.name == "Lisp-like"
        assert config.syntax_options.function_call_start == "("
        assert config.syntax_options.function_call_end == ")"
        
    def test_basic_like_preset(self):
        config = LanguageConfig.from_preset("basic_like")
        assert config.name == "BASIC-like"
        # print is a function, not a keyword
        assert config.builtin_functions["PRINT"].name == "PRINT"
        assert config.syntax_options.array_start_index == 1

    def test_unknown_preset(self):
        with pytest.raises(ValueError):
            LanguageConfig.from_preset("non_existent_preset")
