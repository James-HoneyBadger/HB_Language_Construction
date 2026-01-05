# Language Server Protocol (LSP) Integration Guide

**ParserCraft LSP Support - IDE Integration for Custom Languages**

## Overview

ParserCraft now includes full **Language Server Protocol (LSP)** support, enabling your custom languages to integrate with any modern IDE or text editor:

- **Visual Studio Code**
- **JetBrains IDEs** (PyCharm, IntelliJ, WebStorm, etc.)
- **Neovim / Vim**
- **Sublime Text**
- **Emacs**
- **Any LSP-compatible editor**

## What is LSP?

The Language Server Protocol is a standardized way for code editors to communicate with language-specific tools. Instead of each editor implementing language support separately, you build one **language server** that works with all editors.

## ParserCraft LSP Features

### Core Features

✅ **Syntax Highlighting** - Real-time code coloring
✅ **Code Completion** - IntelliSense for keywords and functions
✅ **Diagnostics** - Error detection and reporting
✅ **Hover Documentation** - Help text on hover
✅ **Signature Help** - Function parameter hints
✅ **Document Symbols** - Quick navigation to functions/definitions
✅ **Workspace Symbols** - Search across all files

### Planned Features

- Go to Definition / Find References
- Rename Symbol Refactoring
- Code Formatting
- Code Actions / Quick Fixes
- Debugging Support

## Quick Start

### 1. Start LSP Server

```bash
# Start server on port 8080
python -m hb_lcs.lsp_server --config my_language.yaml --port 8080

# Or use stdio mode
python -m hb_lcs.lsp_server --config my_language.yaml --stdio
```

### 2. Generate VS Code Extension

```bash
# Generate ready-to-use VS Code extension
python -m hb_lcs.cli extension --config my_language.yaml --output .vscode-ext

# Install dependencies
cd .vscode-ext
npm install

# Compile TypeScript
npm run compile

# Install in VS Code
code --install-extension .
```

### 3. Use in Your IDE

Configure your IDE to use the ParserCraft language server.

## IDE-Specific Setup

### Visual Studio Code

#### Option A: Use Generated Extension (Recommended)

```bash
parsercraft extension --config my_lang.yaml
cd .vscode-ext
npm install && npm run compile
code --install-extension .
```

#### Option B: Manual Configuration

Install LSP Client extension, then add to `.vscode/settings.json`:

```json
{
  "languageServerExample.trace.server": "verbose",
  "[myLanguage]": {
    "editor.defaultFormatter": "parsercraft.my-language"
  },
  "[myLanguage]": {
    "editor.formatOnSave": true
  }
}
```

### JetBrains IDEs (PyCharm, IntelliJ, etc.)

1. Install **LSP Support** plugin
2. Go to **Settings > Languages & Frameworks > Language Server Protocol > Server Definitions**
3. Add new server:
   - Language: `my-language`
   - Extension: `.ml` (or your extension)
   - Server executable: `python -m hb_lcs.lsp_server --config my_language.yaml`

### Neovim

Add to your Neovim config (`init.lua`):

```lua
local lspconfig = require'lspconfig'

local config = {
  cmd = {"python", "-m", "hb_lcs.lsp_server", "--config", "my_language.yaml", "--stdio"},
  filetypes = {"myLanguage"},
  root_dir = require('lspconfig.util').root_pattern(".git", vim.fn.getcwd()),
}

lspconfig.parsercraft_server.setup(config)
```

### Sublime Text

Use **LSP** package. Add to LSP client configuration:

```json
{
  "clients": {
    "parsercraft": {
      "enabled": true,
      "command": ["python", "-m", "hb_lcs.lsp_server", "--config", "my_language.yaml", "--stdio"],
      "languages": {
        "myLanguage": {
          "language_id": "myLanguage",
          "document_selector": "source.myLanguage",
          "document_sync": "full"
        }
      }
    }
  }
}
```

## Python API Usage

Use LSP features programmatically:

```python
from hb_lcs.lsp_server import create_lsp_server, Position
from hb_lcs.language_config import LanguageConfig

# Load your language config
config = LanguageConfig.load("my_language.yaml")

# Create LSP server
server = create_lsp_server("my_language.yaml")

# Open a document
server.handle_did_open("file:///path/to/code.ml", "say 'hello'")

# Get completions
completions = server.completions(
    "file:///path/to/code.ml",
    Position(line=0, character=0)
)

for item in completions:
    print(f"{item['label']}: {item['detail']}")

# Get hover information
hover = server.hover(
    "file:///path/to/code.ml",
    Position(line=0, character=1)
)
if hover:
    print(hover['contents'])

# Get function signature help
sig = server.signature_help(
    "file:///path/to/code.ml",
    Position(line=0, character=5)
)
```

## Architecture

### Components

```
LSPServer
├── DocumentManager          # Manages open documents
├── LanguageServerAnalyzer   # Analyzes code for features
│   ├── Lexer               # Tokenization
│   ├── LanguageValidator   # Validation
│   └── Parser              # AST generation
└── Capabilities            # LSP server capabilities
```

### Request/Response Flow

```
IDE/Editor
    ↓
  JSON-RPC 2.0 Protocol
    ↓
LSP Server ← Parses messages
    ↓
LanguageConfig ← Uses your language definition
    ↓
Parser/Lexer ← Analyzes code
    ↓
Results → Formatted as LSP types
    ↓
  JSON-RPC Response
    ↓
IDE/Editor ← Displays results
```

## LSP Message Examples

### Initialization

**Client → Server:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "rootPath": "/path/to/project",
    "capabilities": {
      "textDocument": {
        "completion": { "completionItem": {} }
      }
    }
  }
}
```

**Server → Client:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "capabilities": {
      "completionProvider": true,
      "hoverProvider": true,
      "definitionProvider": true
    }
  }
}
```

### Code Completion

**Client → Server:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "textDocument/completion",
  "params": {
    "textDocument": { "uri": "file:///path/code.teach" },
    "position": { "line": 0, "character": 3 }
  }
}
```

**Server → Client:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": [
    {
      "label": "when",
      "kind": 1,
      "detail": "keyword",
      "documentation": "Conditional statement"
    },
    {
      "label": "say",
      "kind": 3,
      "detail": "arity: 1",
      "documentation": "Print output"
    }
  ]
}
```

## Extending the LSP Server

### Add Custom Diagnostics

```python
def get_diagnostics(self, content: str) -> list[Diagnostic]:
    diagnostics = super().get_diagnostics(content)
    
    # Add custom checks
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if "deprecated_keyword" in line:
            diagnostics.append(Diagnostic(
                range=Range(
                    start=Position(line=i, character=0),
                    end=Position(line=i, character=len(line))
                ),
                message="deprecated_keyword is deprecated",
                severity=DiagnosticSeverity.WARNING,
                code="DEPRECATED"
            ))
    
    return diagnostics
```

### Add Custom Completions

```python
def get_completions(self, content: str, position: Position) -> list[CompletionItem]:
    completions = super().get_completions(content, position)
    
    # Add snippets
    completions.append(CompletionItem(
        label="if-else block",
        kind=15,  # Snippet
        insert_text="if $1 then\n  $2\nelse\n  $3\nend",
        documentation="Insert if-else statement"
    ))
    
    return completions
```

## Performance Considerations

### Optimization Tips

1. **Incremental Parsing** - Cache ASTs between updates
2. **Lazy Analysis** - Only analyze visible viewport
3. **Token Caching** - Cache tokenization results
4. **Async Processing** - Use asyncio for non-blocking operations

### Example: Incremental Updates

```python
class CachingAnalyzer(LanguageServerAnalyzer):
    def __init__(self, config):
        super().__init__(config)
        self.ast_cache = {}
        self.token_cache = {}
    
    def tokenize(self, content: str) -> list[Token]:
        if content not in self.token_cache:
            self.token_cache[content] = super().tokenize(content)
        return self.token_cache[content]
```

## Debugging

### Enable Verbose Logging

```bash
python -m hb_lcs.lsp_server --config my_lang.yaml --debug
```

Check `lsp_server.log` for detailed information.

### Test LSP Server Directly

```python
import json
from hb_lcs.lsp_server import create_lsp_server

server = create_lsp_server("my_language.yaml")

# Simulate IDE interaction
init = server.initialize(root_path="/project")
print(json.dumps(init, indent=2))

server.handle_did_open(
    "file:///test.teach",
    "say 'hello'"
)
```

## Common Issues & Solutions

### Issue: "Language not found in any LSP server"

**Solution:** Ensure configuration file path is correct and language ID matches.

### Issue: Completions not appearing

**Solution:** Verify trigger characters in LSP capabilities and language configuration.

### Issue: IDE freezes during diagnostics

**Solution:** Optimize `get_diagnostics()` method or increase timeout in IDE settings.

## CLI Commands

```bash
# Start LSP server
parsercraft lsp --config language.yaml --port 8080

# Generate VS Code extension
parsercraft extension --config language.yaml --output .vscode-ext

# List available LSP features
parsercraft info language.yaml

# Validate LSP compatibility
parsercraft validate language.yaml
```

## Integration Examples

### TeachScript IDE Integration

```python
from hb_lcs.lsp_server import create_lsp_server
from hb_lcs.language_config import LanguageConfig

# Load TeachScript config
config = LanguageConfig.load("configs/examples/python_like.yaml")
server = create_lsp_server("configs/examples/python_like.yaml")

# IDE can now use:
# - server.completions(uri, position)
# - server.hover(uri, position)
# - server.get_diagnostics(content)
```

## Resources

- **LSP Specification**: https://microsoft.github.io/language-server-protocol/
- **Language Server Protocol Reference**: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/
- **VS Code Extension Development**: https://code.visualstudio.com/api/
- **ParserCraft Docs**: [docs/guides/CODEX_INTEGRATION_GUIDE.md](../guides/CODEX_INTEGRATION_GUIDE.md)

## Next Steps

1. **Implement Full JSON-RPC Protocol** - Add socket/stdio communication
2. **Add Language Server for Each IDE** - IDE-specific plugins
3. **Extend Diagnostics** - More comprehensive error checking
4. **Add Formatting Support** - Code beautification
5. **Implement Debugging Protocol** - DAP (Debug Adapter Protocol) integration

## Support

For issues or feature requests:
- GitHub Issues: https://github.com/James-HoneyBadger/CodeCraft/issues
- Documentation: See `docs/` folder

---

**Last Updated:** January 2026
**ParserCraft Version:** 2.0.0
