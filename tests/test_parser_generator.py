import pytest
from unittest.mock import MagicMock
from parsercraft.language_config import LanguageConfig, KeywordMapping, OperatorConfig, SyntaxOptions
from parsercraft.parser_generator import Lexer, Token, TokenType, ASTNode

class TestParserGenerator:
    def setup_method(self):
        self.config = LanguageConfig()
        # Setup basic keywords
        self.config.keyword_mappings = {
            "if": KeywordMapping(original="if", custom="si"),
            "function": KeywordMapping(original="def", custom="fun"),
        }
        # Setup operators
        self.config.operators = {
            "+": OperatorConfig(symbol="+", precedence=10),
            "->": OperatorConfig(symbol="->", precedence=20),
        }
        # Setup syntax options
        self.config.syntax_options = SyntaxOptions(single_line_comment="#")

    def test_lexer_keywords_identifiers(self):
        lexer = Lexer(self.config)
        tokens = lexer.tokenize("si x fun y")
        
        # Expected: KEYWORD(si), IDENTIFIER(x), KEYWORD(fun), IDENTIFIER(y), EOF
        assert len(tokens) == 5
        assert tokens[0].type == TokenType.KEYWORD
        assert tokens[0].value == "si"
        assert tokens[1].type == TokenType.IDENTIFIER
        assert tokens[1].value == "x"
        assert tokens[2].type == TokenType.KEYWORD
        assert tokens[2].value == "fun"

    def test_lexer_numbers(self):
        lexer = Lexer(self.config)
        tokens = lexer.tokenize("123 3.14")
        
        assert len(tokens) == 3 # num, num, eof
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "123"
        assert tokens[1].type == TokenType.NUMBER
        assert tokens[1].value == "3.14"

    def test_lexer_strings(self):
        lexer = Lexer(self.config)
        tokens = lexer.tokenize('"hello" \'world\'')
        
        assert len(tokens) == 3
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == '"hello"'
        assert tokens[1].type == TokenType.STRING
        assert tokens[1].value == "'world'"

    def test_lexer_operators(self):
        lexer = Lexer(self.config)
        # Check longest match: if we have -> and -, make sure -> is matched
        # Assuming operators set has -> and +
        tokens = lexer.tokenize("x + y -> z")
        
        # x, +, y, ->, z
        assert tokens[1].type == TokenType.OPERATOR
        assert tokens[1].value == "+"
        assert tokens[3].type == TokenType.OPERATOR
        assert tokens[3].value == "->"

    def test_lexer_punctuation(self):
        lexer = Lexer(self.config)
        tokens = lexer.tokenize("(x, y)")
        
        # (, x, ,, y, )
        values = [t.value for t in tokens if t.type != TokenType.EOF]
        assert values == ["(", "x", ",", "y", ")"]
        assert tokens[0].type == TokenType.PUNCTUATION

    def test_lexer_comments(self):
        lexer = Lexer(self.config)
        tokens = lexer.tokenize("x # This is a comment\ny")
        
        # x, COMMENT, y
        assert tokens[0].value == "x"
        assert tokens[1].type == TokenType.COMMENT
        assert tokens[1].value == "# This is a comment"
        assert tokens[2].value == "y"

    def test_ast_node(self):
        node = ASTNode("BinaryOp", value="+")
        child = ASTNode("Number", value="1")
        node.children.append(child)
        
        d = node.to_dict()
        assert d["type"] == "BinaryOp"
        assert d["value"] == "+"
        assert d["children"][0]["type"] == "Number"
