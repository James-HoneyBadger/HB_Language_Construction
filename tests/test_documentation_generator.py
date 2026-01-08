import unittest
import sys
import os
from pathlib import Path

# Add src to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from parsercraft.language_config import (
    LanguageConfig, KeywordMapping, FunctionConfig, OperatorConfig, SyntaxOptions
)
from parsercraft.documentation_generator import DocumentationGenerator

class TestDocumentationGenerator(unittest.TestCase):
    def setUp(self):
        self.config = LanguageConfig(
            name="TestLang",
            version="1.0",
            description="A test language",
            author="Tester"
        )
        # Add keywords
        self.config.keyword_mappings["if"] = KeywordMapping("if", "si", "control", "Conditional")
        self.config.keyword_mappings["func"] = KeywordMapping("func", "def", "declaration", "Function def")
        
        # Add functions
        self.config.builtin_functions["print"] = FunctionConfig("print", -1, description="Print output")
        self.config.builtin_functions["len"] = FunctionConfig("len", 1, description="Get length", enabled=False)
        
        # Add operators
        self.config.operators["+"] = OperatorConfig("+", 10, "left")
        
        # Syntax options
        self.config.syntax_options = SyntaxOptions(
            array_start_index=0,
            single_line_comment="#",
            multi_line_comment_start="/*",
            allow_fractional_indexing=False
        )

    def test_generate_markdown(self):
        markdown = DocumentationGenerator.generate_markdown(self.config)
        
        # Check Header
        self.assertIn("# TestLang - Language Reference", markdown)
        self.assertIn("**Version**: 1.0", markdown)
        self.assertIn("**Description**: A test language", markdown)
        self.assertIn("**Author**: Tester", markdown)
        
        # Check Keywords
        self.assertIn("| `if` | `si` | control | Conditional |", markdown)
        self.assertIn("| `func` | `def` | declaration | Function def |", markdown)
        
        # Check Functions
        self.assertIn("| `print` | Variadic | ✓ Enabled | Print output |", markdown)
        self.assertIn("| `len` | 1 | ✗ Disabled | Get length |", markdown)
        
        # Check Operators
        self.assertIn("| `+` | 10 | left | ✓ |", markdown)
        
        # Check Syntax Options
        self.assertIn("- **Array Start Index**: 0", markdown)
        self.assertIn("- **Fractional Indexing**: Disabled", markdown)
        self.assertIn("- **Comment Style**: `#`", markdown)
