import pytest
import json
import io
import sys
from unittest.mock import MagicMock, patch
from parsercraft.lsp_server import LSPServer, Position, create_lsp_server
from parsercraft.language_config import LanguageConfig

class TestLSPServer:
    @pytest.fixture
    def server(self):
        config = LanguageConfig()
        return LSPServer(config)

    def test_handle_initialize(self, server):
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        response = server._handle_request(request)
        assert response["id"] == 1
        assert "capabilities" in response["result"]

    def test_handle_shutdown(self, server):
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "shutdown"
        }
        response = server._handle_request(request)
        assert response["result"] is None

    def test_hover_no_content(self, server):
        position = Position(line=0, character=0)
        # Use analyzer directly for this low-level test
        hover = server.analyzer.get_hover_info("", position)
        assert hover is None

    @patch('sys.stdin', new_callable=io.StringIO)
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_run_stdio(self, mock_stdout, mock_stdin, server):
        # Prepare input: Content-Length header + JSON body
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        body = json.dumps(request)
        message = f"Content-Length: {len(body)}\r\n\r\n{body}"
        
        # We need to break the loop, so we mock _handle_request to raise an exception after processing
        # Or simpler: feed input, then EOF.
        mock_stdin.write(message)
        mock_stdin.seek(0)
        
        # Run server (it will process one message then stop on EOF)
        server.run_stdio()
        
        # Check output
        output = mock_stdout.getvalue()
        assert "Content-Length:" in output
        assert "capabilities" in output

    def test_completion(self, server):
        # Add a keyword to config
        server.config.rename_keyword("if", "when")
        
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "textDocument/completion",
            "params": {
                "textDocument": {"uri": "file:///test.txt"},
                "position": {"line": 0, "character": 0}
            }
        }
        response = server._handle_request(request)
        items = response["result"]["items"]
        assert any(item["label"] == "when" for item in items)
