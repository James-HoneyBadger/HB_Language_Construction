import unittest
import sys
import os

# Add src to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from parsercraft.identifier_validator import IdentifierValidator

class TestIdentifierValidator(unittest.TestCase):

    def test_is_valid_identifier(self):
        self.assertTrue(IdentifierValidator.is_valid_identifier("valid_name"))
        self.assertTrue(IdentifierValidator.is_valid_identifier("_valid"))
        self.assertTrue(IdentifierValidator.is_valid_identifier("valid123"))
        self.assertFalse(IdentifierValidator.is_valid_identifier("1invalid"))
        self.assertFalse(IdentifierValidator.is_valid_identifier("no space"))
        self.assertFalse(IdentifierValidator.is_valid_identifier(""))

    def test_is_valid_length(self):
        self.assertTrue(IdentifierValidator.is_valid_length("a", 1, 10))
        self.assertTrue(IdentifierValidator.is_valid_length("aaa", 1, 10))
        self.assertTrue(IdentifierValidator.is_valid_length("aaaaaaaaaa", 1, 10))
        self.assertFalse(IdentifierValidator.is_valid_length("", 1, 10))
        self.assertFalse(IdentifierValidator.is_valid_length("aaaaaaaaaaa", 1, 10))

    def test_is_python_reserved(self):
        self.assertTrue(IdentifierValidator.is_python_reserved("if"))
        self.assertTrue(IdentifierValidator.is_python_reserved("class"))
        self.assertTrue(IdentifierValidator.is_python_reserved("None"))
        self.assertFalse(IdentifierValidator.is_python_reserved("my_var"))

    def test_detect_naming_style(self):
        self.assertEqual(IdentifierValidator.detect_naming_style("snake_case"), "snake_case")
        self.assertEqual(IdentifierValidator.detect_naming_style("camelCase"), "camelCase")
        self.assertEqual(IdentifierValidator.detect_naming_style("PascalCase"), "PascalCase")
        self.assertEqual(IdentifierValidator.detect_naming_style("SCREAMING_CASE"), "SCREAMING_SNAKE_CASE")
        # Mixed/Invalid styles
        self.assertIsNone(IdentifierValidator.detect_naming_style("weird_MixingOfStyles"))
    
    def test_validate_identifier_basic(self):
        valid, warnings = IdentifierValidator.validate_identifier("nice_name")
        self.assertTrue(valid)
        self.assertEqual(len(warnings), 0)

        valid, warnings = IdentifierValidator.validate_identifier("1bad")
        self.assertFalse(valid)
        self.assertIn("'1bad' is not a valid identifier", warnings)

    def test_validate_identifier_reserved(self):
        # By default not allowed
        valid, warnings = IdentifierValidator.validate_identifier("if")
        self.assertFalse(valid)
        self.assertIn("'if' is a Python reserved word", warnings)

        # Allow reserved
        valid, warnings = IdentifierValidator.validate_identifier("if", allow_reserved=True)
        self.assertTrue(valid)
        self.assertIn("'if' is a Python reserved word (may cause issues)", warnings)

    def test_validate_identifier_reserved_set(self):
        reserved = {"existing"}
        valid, warnings = IdentifierValidator.validate_identifier("existing", reserved_set=reserved)
        self.assertFalse(valid)
        self.assertIn("'existing' conflicts with existing identifier", warnings)

    def test_validate_identifier_style_warning(self):
        valid, warnings = IdentifierValidator.validate_identifier("Weird_Style")
        self.assertTrue(valid)
        self.assertTrue(any("non-standard naming" in w for w in warnings))

