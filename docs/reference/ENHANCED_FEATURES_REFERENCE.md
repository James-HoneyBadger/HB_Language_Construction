# Enhanced Features Technical Reference

**ParserCraft v2.0.0 - New System APIs and Architecture**

## Quick API Reference

### LSP Server

```python
from hb_lcs.lsp_server import create_lsp_server, Position, Range, Diagnostic
from hb_lcs.language_config import LanguageConfig

# Create and use LSP server
server = create_lsp_server("language.yaml")

# Open/edit documents
server.handle_did_open("file:///code.lang", content)
server.handle_did_change("file:///code.lang", changes, version)
server.handle_did_close("file:///code.lang")

# Get IDE features
completions = server.completions("file:///code.lang", Position(line=0, char=0))
hover = server.hover("file:///code.lang", Position(line=0, char=5))
signature = server.signature_help("file:///code.lang", Position(line=0, char=10))
symbols = server.document_symbols("file:///code.lang")
diagnostics = server.get_diagnostics(content)

# Initialize server
capabilities = server.initialize("/project/root")
```

### VS Code Extension

```python
from hb_lcs.vscode_integration import (
    generate_vscode_extension,
    generate_simple_grammar
)

config = LanguageConfig.load("my_lang.yaml")

# Generate full extension
generate_vscode_extension(
    config=config,
    output_dir=".vscode-ext",
    publisher="mypub",
    version="1.0.0"
)

# Generate grammar reference
generate_simple_grammar(config, "grammar.txt")
```

### Module System

```python
from hb_lcs.module_system import (
    ModuleManager,
    ModuleImport,
    ModuleExport,
    Module
)
from hb_lcs.language_config import LanguageConfig

# Create manager
config = LanguageConfig.load("language.yaml")
manager = ModuleManager(
    config=config,
    search_paths=["./lib", "./modules"],
    enable_caching=True
)

# Load modules
module = manager.load_module("math_utils")
modules = manager.load_with_dependencies("main")

# Get information
info = manager.get_module_info("math_utils")
dependencies = manager.resolve_dependencies("main")
cycles = manager.detect_circular_dependencies()

# Export analysis
manager.export_dependency_graph("deps.json")

# Module details
module.add_export(ModuleExport(
    name="calculate",
    kind="function",
    documentation="Calculate value"
))
```

## CLI Reference

### LSP Commands

```bash
# Start Language Server Protocol server
parsercraft lsp --config language.yaml [--port 8080] [--stdio]

# Generate VS Code extension
parsercraft extension --config language.yaml \
  [--output .vscode-ext] \
  [--publisher mypub] \
  [--version 1.0.0]
```

### Module Commands

```bash
# Get module information
parsercraft module-info mymodule

# List module dependencies
parsercraft module-deps main.lang

# Detect circular dependencies
parsercraft module-cycles ./project

# Export dependency graph
parsercraft module-graph main.lang --output deps.json

# Create module template
parsercraft module-create newmodule [--template basic|library]

# Package module for distribution
parsercraft module-package mymodule

# Publish to registry
parsercraft module-publish mymodule --registry https://registry.io
```

## File Formats

### Language Configuration (YAML)

```yaml
name: MyLanguage
version: 1.0.0
author: Your Name

syntax:
  line_comment: "#"
  block_comment: ["/*", "*/"]
  string_delimiters: ['"', "'"]

keywords:
  when:
    original: "if"
    category: "control"
  teach:
    original: "def"
    category: "function"

functions:
  say:
    arity: 1
    description: "Output to console"
  print:
    arity: -1  # variadic
    description: "Print values"
```

### Module File (module.yaml)

```yaml
name: my-library
version: 1.0.0
description: "Library description"
author: Author Name
license: MIT

entry_point: main.lang

exports:
  math: math.lang
  graphics: graphics.lang
  utils: utils.lang

dependencies:
  base-lib: "^1.0.0"
  graphics: "2.x"
  optional-lib: { version: "1.0.0", optional: true }

dev_dependencies:
  test-framework: "^1.0.0"

keywords:
  - math
  - utilities
```

### Module in Source File

```teach
#@ version: 1.0.0
#@ author: Jane Doe
#@ description: Mathematical utilities
#@ license: MIT
#@ homepage: https://example.com

import base_utils
import graphics version "^2.0.0"

# Private helper
function _validate(x)
    # ...
end

# Public API
export function calculate(x)
    return _validate(x) * 2
end

export const VERSION = "1.0.0"
```

## Architecture Diagrams

### LSP Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    IDE / Editor                         │
│        (VS Code, PyCharm, Neovim, etc.)                 │
└────────────────────┬────────────────────────────────────┘
                     │ JSON-RPC 2.0
                     │ over Socket/Stdio
┌────────────────────▼────────────────────────────────────┐
│              LSP Server Instance                        │
│  ┌──────────────────────────────────────────────┐      │
│  │ LSPServer                                    │      │
│  │ ├── DocumentManager                          │      │
│  │ │   ├── Open documents                       │      │
│  │ │   └── Incremental updates                  │      │
│  │ ├── LanguageServerAnalyzer                   │      │
│  │ │   ├── Lexer (tokenization)                 │      │
│  │ │   ├── get_completions()                    │      │
│  │ │   ├── get_diagnostics()                    │      │
│  │ │   ├── get_hover_info()                     │      │
│  │ │   └── get_symbols()                        │      │
│  │ └── Capabilities                             │      │
│  │     ├── completionProvider: true             │      │
│  │     ├── hoverProvider: true                  │      │
│  │     └── ...                                  │      │
│  └──────────────────────────────────────────────┘      │
│                     ▼                                   │
│  ┌──────────────────────────────────────────────┐      │
│  │ Language Configuration & Runtime             │      │
│  │ ├── Keywords                                 │      │
│  │ ├── Functions                                │      │
│  │ └── Syntax Options                           │      │
│  └──────────────────────────────────────────────┘      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
        Results formatted as LSP types
```

### Module System Architecture

```
┌─────────────────────────────────────────┐
│         Main Program                    │
│         (main.teach)                    │
└────────┬────────────────────────────────┘
         │ import math, graphics
         ▼
┌──────────────────────────────────────────────────────┐
│       ModuleManager                                  │
│  ┌────────────────────────────────────────────────┐  │
│  │ load_module("math")                            │  │
│  │ load_module("graphics")                        │  │
│  │ load_with_dependencies("main")                 │  │
│  │ detect_circular_dependencies()                 │  │
│  └────────────────────────────────────────────────┘  │
└────┬──────────────────────────────────────────────────┘
     │
     ├─────────────────┬──────────────────┬──────────────┐
     ▼                 ▼                  ▼              ▼
┌─────────┐    ┌───────────────┐  ┌──────────────┐  ┌──────────┐
│  math   │    │  graphics     │  │ base_utils   │  │ external │
│ .teach  │    │ .teach        │  │ .teach       │  │ _lib/... │
└─────────┘    └───────────────┘  └──────────────┘  └──────────┘
     │                │                  │
     │ Exports        │ Exports          │ Exports
     ▼                ▼                  ▼
  {sin,           {draw,             {format,
   cos,            rect}               split}
   PI}
```

### Module Dependency Resolution

```
main.teach
  ├── import math
  │    └── no dependencies
  │
  ├── import graphics
  │    └── import colors
  │         └── no dependencies
  │
  └── import utils
       ├── import base
       │    └── no dependencies
       └── import math (already loaded)

Resolved order: base → colors → math → graphics → utils → main
```

## Error Handling

### LSP Errors

```python
from hb_lcs.lsp_server import LSPServer, DiagnosticSeverity, Diagnostic

# Syntax errors
diagnostic = Diagnostic(
    range=Range(start, end),
    message="Unmatched string quote",
    severity=DiagnosticSeverity.ERROR,
    code="E001"
)

# Warnings
diagnostic = Diagnostic(
    range=Range(start, end),
    message="Deprecated keyword",
    severity=DiagnosticSeverity.WARNING,
    code="W001"
)

# Info
diagnostic = Diagnostic(
    range=Range(start, end),
    message="Unused variable",
    severity=DiagnosticSeverity.INFORMATION,
    code="I001"
)
```

### Module System Errors

```python
from hb_lcs.module_system import (
    ModuleNotFoundError,
    ModuleLoadError,
    CircularDependencyError
)

try:
    module = manager.load_module("nonexistent")
except ModuleNotFoundError:
    print("Module not found in search paths")

try:
    modules = manager.load_with_dependencies("main")
except ModuleLoadError:
    print("Error loading module content")

# Detect cycles
cycles = manager.detect_circular_dependencies()
if cycles:
    raise CircularDependencyError(f"Cycles: {cycles}")
```

## Configuration Examples

### Simple Language Config

```python
from hb_lcs.language_config import LanguageConfig, KeywordMapping

config = LanguageConfig()
config.name = "MyLang"
config.version = "1.0.0"

# Add keywords
config.keyword_mappings["mi_si"] = KeywordMapping(
    original="if",
    custom="mi_si",
    category="control"
)

config.save("my_lang.yaml")
```

### Create Module

```python
from hb_lcs.module_system import Module, ModuleExport, ModuleVisibility

module = Module(
    name="math_utils",
    path=Path("math_utils.teach"),
    content="...",
    language_config=config
)

# Add exports
module.add_export(ModuleExport(
    name="square",
    kind="function",
    visibility=ModuleVisibility.PUBLIC,
    documentation="Calculate square of number"
))

module.version = "1.0.0"
module.author = "Jane Doe"
```

## Performance Tips

### LSP Optimization

```python
from hb_lcs.lsp_server import LanguageServerAnalyzer

class OptimizedAnalyzer(LanguageServerAnalyzer):
    def __init__(self, config):
        super().__init__(config)
        self._diagnostic_cache = {}
    
    def get_diagnostics(self, content):
        # Cache expensive diagnostics
        cache_key = hash(content)
        if cache_key in self._diagnostic_cache:
            return self._diagnostic_cache[cache_key]
        
        diagnostics = super().get_diagnostics(content)
        self._diagnostic_cache[cache_key] = diagnostics
        return diagnostics
```

### Module Optimization

```python
# Disable caching for development
manager = ModuleManager(config, enable_caching=False)

# Enable caching for production
manager = ModuleManager(config, enable_caching=True)

# Clear cache periodically
if time.time() - last_clear > 3600:  # 1 hour
    manager.loader.cache.clear()
```

## Extension Points

### Custom Analyzer

```python
class CustomAnalyzer(LanguageServerAnalyzer):
    def get_diagnostics(self, content):
        diagnostics = super().get_diagnostics(content)
        
        # Add domain-specific checks
        if "deprecated" in content:
            # Custom check
            pass
        
        return diagnostics
```

### Custom Loader

```python
class CustomLoader(ModuleLoader):
    def _parse_module(self, module):
        super()._parse_module(module)
        
        # Custom parsing
        # e.g., extract type annotations
        pass
```

### Custom Module Manager

```python
class CustomManager(ModuleManager):
    def load_module(self, module_name, search_relative_to=None):
        # Custom loading logic
        # e.g., from remote repository
        return super().load_module(module_name, search_relative_to)
```

## Debugging

### Enable LSP Logging

```bash
python -m hb_lcs.lsp_server --config lang.yaml --debug
# Check: lsp_server.log
```

### Module Debugging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

manager = ModuleManager(config)
modules = manager.load_with_dependencies("main")
```

### Inspect Module State

```python
# Get module info
module = manager.load_module("math")
print(module.to_dict())

# Inspect exports
for name, export in module.exports.items():
    print(f"{name}: {export.kind}")

# Check dependencies
for dep in module.dependencies:
    print(f"depends on: {dep.module_name}")
```

## Testing

### Test LSP Server

```python
def test_lsp_completion():
    server = create_lsp_server("test.yaml")
    server.handle_did_open("file:///test", "when ")
    
    completions = server.completions(
        "file:///test",
        Position(line=0, character=5)
    )
    
    assert any(c['label'] == 'when' for c in completions)
```

### Test Module System

```python
def test_module_loading():
    manager = ModuleManager(config, search_paths=["./test_modules"])
    module = manager.load_module("test_module")
    
    assert module.name == "test_module"
    assert "hello" in module.exports
```

---

**Last Updated:** January 4, 2026
**ParserCraft Version:** 2.0.0
