import pytest
from unittest.mock import MagicMock, patch
from src.parsercraft.test_framework import (
    TestCase, TestResult, LanguageTestRunner
)
from src.parsercraft.language_config import LanguageConfig
from src.parsercraft.ast_integration import ASTNode

class MockParserGen:
    def __init__(self, config):
        pass
    def parse(self, code):
        Token = MagicMock()
        Token.type.value = "ID"
        return [Token], ASTNode(node_type="program")

def test_runner_execution_failure():
    config = LanguageConfig(name="TestLang")
    runner = LanguageTestRunner(config)
    runner.parser_gen = MockParserGen(config)
    
    # "si True" is not valid Python, will fail exec()
    case = TestCase(name="test1", code="si True")
    
    try:
        runner.run_test(case)
    except SyntaxError:
        pass # Expected
    except NameError:
        pass # Expected

def test_runner_execution_success_python():
    config = LanguageConfig(name="TestLang")
    runner = LanguageTestRunner(config)
    runner.parser_gen = MockParserGen(config)
    
    case = TestCase(name="test2", code="print('hello')", expected_output="hello\n")
    
    result = runner.run_test(case)
    # Note: result depends on stdout capture
    assert result.passed
    assert result.output.strip() == "hello"

