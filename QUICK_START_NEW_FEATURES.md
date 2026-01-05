# ParserCraft 2.0.0 - Quick Start for New Features

## 🚀 Language Server Protocol (LSP) - IDE Integration

### Generate a VS Code Extension (90 seconds)

```bash
# Create VS Code extension for your language
parsercraft extension --config my_language.yaml --output .vscode-ext

# Install dependencies
cd .vscode-ext && npm install

# Compile and install
npm run compile
code --install-extension .
```

**That's it!** Your language now has:
- ✅ Syntax highlighting
- ✅ Code completion (Ctrl+Space)
- ✅ Error checking
- ✅ Hover help
- ✅ Function signatures

### Use in Other IDEs

```bash
# Start LSP server
parsercraft lsp --config my_language.yaml --port 8080

# Now configure your IDE to connect to localhost:8080
# Works with: PyCharm, Neovim, Vim, Sublime, Emacs, etc.
```

---

## 📦 Module & Package System - Multi-file Programs

### Create Your First Module

Create `math.teach`:
```teach
#@ version: 1.0.0
#@ description: Math utilities

export function square(x)
    return x * x
end

export function cube(x)
    return x * x * x
end
```

Create `main.teach`:
```teach
import math

say math.square(5)   # 25
say math.cube(3)     # 27
```

Run it:
```bash
parsercraft run main.teach
```

### Organize Large Projects

```
project/
├── main.teach
├── modules/
│   ├── math.teach
│   ├── graphics.teach
│   └── utils.teach
└── lib/
    └── external_lib/
```

Import from modules:
```teach
import modules.math as math
import modules.graphics as gfx
```

### Check Dependencies

```bash
# View module dependencies
parsercraft module-info modules.math

# Check all project dependencies
parsercraft module-deps main.teach

# Detect circular dependencies
parsercraft module-cycles ./project/

# Visualize dependencies
parsercraft module-graph main.teach --output deps.json
```

---

## 📚 Documentation Links

| Feature | Guide |
|---------|-------|
| **LSP Setup** | [docs/guides/LSP_INTEGRATION_GUIDE.md](docs/guides/LSP_INTEGRATION_GUIDE.md) |
| **Modules** | [docs/guides/MODULE_SYSTEM_GUIDE.md](docs/guides/MODULE_SYSTEM_GUIDE.md) |
| **API Reference** | [docs/reference/ENHANCED_FEATURES_REFERENCE.md](docs/reference/ENHANCED_FEATURES_REFERENCE.md) |
| **Full Summary** | [docs/HIGH_IMPACT_ENHANCEMENTS_SUMMARY.md](docs/HIGH_IMPACT_ENHANCEMENTS_SUMMARY.md) |

---

## 💡 Example: TeachScript with IDE Support

```bash
# Generate VS Code extension for TeachScript
parsercraft extension --config configs/examples/python_like.yaml \
  --output .vscode-ext/teachscript \
  --publisher parsercraft \
  --version 1.0.0

# Install it
cd .vscode-ext/teachscript
npm install && npm run compile
code --install-extension .
```

Now create `hello.teach`:
```teach
teach hello()
    say "Hello, World!"
end

hello()
```

Open in VS Code → Full IDE support! 🎉

---

## 🔧 Python API Examples

### Use LSP Programmatically

```python
from hb_lcs.lsp_server import create_lsp_server, Position

server = create_lsp_server("my_language.yaml")
server.handle_did_open("file:///code.lang", "say ")

# Get completions
completions = server.completions(
    "file:///code.lang",
    Position(line=0, character=4)
)

# Get hover info
hover = server.hover(
    "file:///code.lang",
    Position(line=0, character=1)
)

# Get diagnostics
diagnostics = server.get_diagnostics("say 'hello'")
```

### Use Module System Programmatically

```python
from hb_lcs.module_system import ModuleManager
from hb_lcs.language_config import LanguageConfig

config = LanguageConfig.load("my_language.yaml")
manager = ModuleManager(config, search_paths=["./lib", "./modules"])

# Load module and all its dependencies
modules = manager.load_with_dependencies("main")

for name, module in modules.items():
    print(f"{name}: {module.description}")
    for export_name, export in module.exports.items():
        print(f"  - {export_name} ({export.kind})")

# Check for circular dependencies
cycles = manager.detect_circular_dependencies()
if cycles:
    print(f"Warning: {cycles}")
```

---

## ⚡ Quick Commands Cheat Sheet

```bash
# Extension & LSP
parsercraft extension --config lang.yaml --output .vscode-ext
parsercraft lsp --config lang.yaml --port 8080

# Modules
parsercraft module-info mymodule
parsercraft module-deps main.teach
parsercraft module-cycles ./project
parsercraft module-graph main.teach --output deps.json
```

---

## 🎯 What's Next?

The next 2 high-impact features planned are:

1. **Type System & Static Analysis** - Add type annotations and static type checking
2. **Compiler Backends** - Compile to C, WASM, or native executables

Stay tuned! 🚀

---

**Version:** ParserCraft 2.0.0  
**Date:** January 4, 2026
