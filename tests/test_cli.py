import pytest
from unittest.mock import MagicMock, patch
import argparse
import sys
from io import StringIO
from pathlib import Path

# Import handlers by importing cli module
# Since cli.py has many imports, we assume it's importable
from parsercraft import cli
from parsercraft.language_config import LanguageConfig

class TestCLI:
    
    def test_cmd_list_presets(self, capsys):
        # cmd_list_presets takes args but ignores them
        args = MagicMock()
        
        # We need to verify if calling cmd_list_presets works
        # And prints something
        
        result = cli.cmd_list_presets(args)
        assert result == 0
        
        captured = capsys.readouterr()
        assert "Available Presets:" in captured.out
        assert "python_like" in captured.out

    def test_cmd_create_preset(self, tmp_path):
        output_file = tmp_path / "new_lang.yaml"
        args = argparse.Namespace(
            preset="python_like",
            output=str(output_file),
            interactive=False
        )
        
        result = cli.cmd_create(args)
        assert result == 0
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "Language Configuration" in content or "metadata" in content

    @patch('parsercraft.cli.create_custom_config_interactive')
    def test_cmd_create_interactive(self, mock_interactive, tmp_path):
        output_file = tmp_path / "interactive.yaml"
        args = argparse.Namespace(
            preset=None,
            output=str(output_file),
            interactive=True
        )
        
        # Mock interactive creation to return a config
        mock_config = LanguageConfig(name="InteractiveLang")
        mock_interactive.return_value = mock_config
        
        result = cli.cmd_create(args)
        assert result == 0
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "InteractiveLang" in content

    def test_cmd_validate_valid(self, tmp_path):
        # Create a valid config file
        p = tmp_path / "valid.yaml"
        config = LanguageConfig(name="ValidLang")
        config.save(p)
        
        args = argparse.Namespace(file=str(p))
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            result = cli.cmd_validate(args)
            assert result == 0
            assert "Configuration is valid" in fake_out.getvalue()

    def test_cmd_validate_missing_file(self):
        args = argparse.Namespace(file="nonexistent.yaml")
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            result = cli.cmd_validate(args)
            assert result == 1
            assert "Error" in fake_out.getvalue()

    def test_cmd_info(self, tmp_path, capsys):
        p = tmp_path / "info_lang.yaml"
        config = LanguageConfig(name="InfoLang", version="3.0")
        config.save(p)
        
        args = argparse.Namespace(file=str(p))
        
        result = cli.cmd_info(args)
        assert result == 0
        
        captured = capsys.readouterr()
        assert "InfoLang" in captured.out
        assert "3.0" in captured.out
