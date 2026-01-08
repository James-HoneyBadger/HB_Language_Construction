import pytest
from parsercraft.language_config import LanguageConfig, KeywordMapping, FunctionConfig, OperatorConfig
from parsercraft.language_validator import LanguageValidator, ValidationIssue

class TestLanguageValidator:
    def test_duplicate_keywords(self):
        config = LanguageConfig()
        # "if" -> "dupe_one", "while" -> "dupe_one" (Duplicate!)
        config.keyword_mappings = {
            "if": KeywordMapping(original="if", custom="dupe_one"),
            "while": KeywordMapping(original="while", custom="dupe_one"),
        }
        
        validator = LanguageValidator(config)
        validator.check_keyword_conflicts()
        
        # We expect 1 duplicate error.
        assert len(validator.issues) == 1
        assert "Duplicate keyword" in validator.issues[0].message
        assert validator.issues[0].severity == "error"

    def test_function_keyword_conflict(self):
        config = LanguageConfig()
        # keyword "print" -> "imprimir"
        # function "imprimir"
        config.keyword_mappings = {
            "print": KeywordMapping(original="print", custom="imprimir")
        }
        config.builtin_functions = {
            "imprimir": FunctionConfig(name="imprimir", arity=1)
        }
        
        validator = LanguageValidator(config)
        validator.check_function_conflicts()
        
        assert len(validator.issues) == 1
        assert "conflicts with keyword" in validator.issues[0].message

    def test_operator_precedence_mixed_associativity(self):
        config = LanguageConfig()
        config.operators = {
            "+": OperatorConfig(symbol="+", precedence=10, associativity="left"),
            "-": OperatorConfig(symbol="-", precedence=10, associativity="right"),
        }
        
        validator = LanguageValidator(config)
        validator.check_operator_precedence()
        
        assert len(validator.issues) == 1
        assert "mixed associativity" in validator.issues[0].message
        assert validator.issues[0].severity == "warning"

    def test_function_arity_check(self):
        config = LanguageConfig()
        config.builtin_functions = {
            "bad": FunctionConfig(name="bad", arity=-2) # Invalid arity
        }
        
        validator = LanguageValidator(config)
        validator.check_function_conflicts() # This method checks arity too
        
        # We might have warnings about conflict if "bad" name is not handled, 
        # but here we focus on arity error.
        arity_issues = [i for i in validator.issues if i.category == "invalid_arity"]
        assert len(arity_issues) == 1

    def test_clean_config(self):
        config = LanguageConfig() 
        # Default config should be valid
        validator = LanguageValidator(config)
        issues = validator.validate_all()
        # Note: Default config might have Info warnings or such, but no Errors.
        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) == 0
