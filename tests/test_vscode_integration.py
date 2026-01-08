import pytest
import json
from parsercraft.vscode_integration import generate_vscode_extension
from parsercraft.language_config import LanguageConfig, SyntaxOptions

class TestVSCodeIntegration:
    def test_generate_extension(self, tmp_path):
        config = LanguageConfig(name="TestLang")
        # Setup specific comment style
        config.syntax_options = SyntaxOptions(
            single_line_comment="//",
            multi_line_comment_start="/*",
            multi_line_comment_end="*/"
        )
        
        output_dir = tmp_path / "ext"
        generate_vscode_extension(
            config, 
            output_dir=str(output_dir), 
            publisher="tester",
            version="1.0"
        )
        
        # Check files created
        assert (output_dir / "package.json").exists()
        assert (output_dir / "language-configuration.json").exists()
        
        # Check language-configuration.json content
        lang_config_file = output_dir / "language-configuration.json"
        data = json.loads(lang_config_file.read_text())
        
        # This will fail if vscode_integration.py uses wrong attribute names
        assert data["comments"]["lineComment"] == "//"
        assert data["comments"]["blockComment"] == ["/*", "*/"]
