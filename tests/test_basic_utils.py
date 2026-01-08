import pytest
from parsercraft.identifier_validator import IdentifierValidator
from parsercraft.documentation_generator import DocumentationGenerator
from parsercraft.language_config import LanguageConfig

class TestIdentifierValidator:
    def test_is_valid_identifier(self):
        assert IdentifierValidator.is_valid_identifier("good_id")
        assert IdentifierValidator.is_valid_identifier("GoodId")
        assert IdentifierValidator.is_valid_identifier("GOOD_ID")
        assert not IdentifierValidator.is_valid_identifier("1bad")
        assert not IdentifierValidator.is_valid_identifier("bad-id")
        assert not IdentifierValidator.is_valid_identifier("")

    def test_is_valid_length(self):
        assert IdentifierValidator.is_valid_length("abc", 1, 3)
        assert IdentifierValidator.is_valid_length("a", 1, 3)
        assert not IdentifierValidator.is_valid_length("", 1, 3)
        assert not IdentifierValidator.is_valid_length("abcd", 1, 3)

    def test_is_python_reserved(self):
        assert IdentifierValidator.is_python_reserved("if")
        assert IdentifierValidator.is_python_reserved("class")
        assert not IdentifierValidator.is_python_reserved("my_var")

    def test_detect_naming_style(self):
        assert IdentifierValidator.detect_naming_style("snake_case") == "snake_case"
        assert IdentifierValidator.detect_naming_style("camelCase") == "camelCase"
        assert IdentifierValidator.detect_naming_style("PascalCase") == "PascalCase"
        assert IdentifierValidator.detect_naming_style("SCREAMING_SNAKE_CASE") == "SCREAMING_SNAKE_CASE"
        assert IdentifierValidator.detect_naming_style("invalid-case") is None

    def test_validate_identifier(self):
        # Basic validation
        valid, msg = IdentifierValidator.validate_identifier("valid_name")
        assert valid
        assert msg == []

        # Invalid chars
        valid, msg = IdentifierValidator.validate_identifier("invalid-name")
        assert not valid
        assert any("not a valid" in m for m in msg)

        # Reserved word
        valid, msg = IdentifierValidator.validate_identifier("if", allow_reserved=False)
        assert not valid
        assert any("reserved" in m for m in msg)

        # Reserved word allowed
        valid, msg = IdentifierValidator.validate_identifier("if", allow_reserved=True)
        assert valid

class TestDocumentationGenerator:
    def test_generate_markdown(self):
        config = LanguageConfig(name="TestLang", version="1.0.0")
        config.rename_keyword("if", "si")
        config.syntax_options.array_start_index = 0
        
        md = DocumentationGenerator.generate_markdown(config)
        
        assert "# TestLang - Language Reference" in md
        assert "Version: 1.0.0" in md.replace("**", "") # Simplified check
        assert "| `if` | `si` |" in md
        assert "**Array Start Index**: 0" in md
